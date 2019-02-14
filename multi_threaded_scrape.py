# take in a sql database with a list of URLs and scrape each url,
# adding the text of the page to the database. Database format is:
# Table name: Tasks
# Columns:
#     url TEXT NOT NULL UNIQUE,
#     completed BOOLEAN NOT NULL CHECK (completed IN(0,1)),
#     page_text STRING,
#     identified_timestamp DATETIME default current_timestamp,
#     scraped_timestamp DATETIME

from queue import Queue
import requests
from threading import Thread, Lock
from create_tasks_database import create_tasks_database
from datetime import datetime
import sqlite3
import os
import subprocess
from create_multiple_torrc_files import create_torrc_files


THREADS_PER_SESSION = 10
NUMBER_OF_SESSIONS = 10

# todo - this may be very inefficient
# todo - consider saving progress in chunks
def mark_task_completed(conn, page_text, url):
    global lck
    lck.acquire()
    c = conn.cursor()
    c.execute("UPDATE Tasks SET completed = ? WHERE url = ?", (1, url))
    c.execute("UPDATE Tasks SET page_text = ? WHERE url = ?", (page_text, url))
    c.execute("UPDATE Tasks SET scraped_timestamp = ? WHERE url = ?", (datetime.utcnow(), url))
    print("scraped {}".format(url))
    conn.commit()
    lck.release()


def scrape(q, conn):
    while not q.empty():
        work = q.get()
        try:
            page_text = requests.get(work[1]).text
        except requests.exceptions.RequestException as e:
            page_text = e
        mark_task_completed(conn, page_text, work[1])
        q.task_done()
    return True


current_dir = os.path.dirname(os.path.realpath(__file__))
torrcs = create_torrc_files(NUMBER_OF_SESSIONS, current_dir)

# todo - test the following
sessions = []
for torrc in torrcs:
    subprocess.call(['sudo', 'tor', '-f', torrc["path"]])
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:{}'.format(torrc["SOCKSPort"])
    session.proxies['https'] = 'socks5h://localhost:{}'.format(torrc["SOCKSPort"])
    sessions.append(session)

# todo - run a test to confirm that all subprocesses are working and have unique IPs.
# todo - if any are not working or have the same IP, get new identity (max retries = 5 or so)

db_filepath = create_tasks_database()
conn = sqlite3.connect(db_filepath, check_same_thread=False)
conn.row_factory = lambda cursor, row: row[0]
c = conn.cursor()
urls = c.execute("SELECT url FROM Tasks WHERE completed == 0").fetchall()

lck = Lock()
    
q = Queue(maxsize=0)

num_threads = min(50, len(urls))

# fill task queue
for i in range(len(urls)):
    q.put((i, urls[i]))
    
# This would make X threads per session
for session in sessions:
    for i in range(THREADS_PER_SESSION):
        worker = Thread(target=scrape, args=(session,q,conn))
        worker.setDaemon(True)
        worker.start()
q.join()
conn.close()
