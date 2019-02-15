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
from tor_session import TorSession


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


def scrape(tor_session, q, conn):
    while not q.empty():
        work = q.get()
        try:
            page_text = tor_session.get(work[1]).text
        except requests.exceptions.RequestException as e:
            page_text = e
        mark_task_completed(conn, page_text, work[1])
        q.task_done()
    return True


tor_sessions = []
tor_dir = "etc/tor/"
for i in range(NUMBER_OF_SESSIONS):

    SOCKSPort = 40000 + i
    ControlPort = 41000 + i

    torrc_dir = os.path.join(tor_dir, "torrc.{}".format(i))

    tor_session = TorSession(SOCKSPort=SOCKSPort,
                             ControlPort=ControlPort,
                             torrc_dir=torrc_dir)
    tor_sessions.append(tor_session)

# for each session, ensure IP is unique.
# for duplicates, get new identity
# max retries for each duplicate = 5
# after max retries, remove the session from the list of sessions
ips = []
for tor_session in tor_sessions:
    ip = tor_session.ip
    retries = 0
    while True:
        if ip not in ips:
            break
        elif retries > 4:
            tor_sessions.remove(tor_session)
            print("A Tor session was removed after failing to acquire a unique identity")
            break
        ip = tor_session.get_new_identity()
        retries += 1
    ips.append(ip)

db_filepath = create_tasks_database()
conn = sqlite3.connect(db_filepath, check_same_thread=False)
# modifying conn.row_factory modifies how sqlite will return values when running queries.
# specifically, it forces it to return a list instead of a list of tuples
conn.row_factory = lambda cursor, row: row[0]
c = conn.cursor()
urls = c.execute("SELECT url FROM Tasks WHERE completed == 0").fetchall()

lck = Lock()
    
q = Queue(maxsize=0)

# fill task queue
for i in range(len(urls)):
    q.put((i, urls[i]))
    
for tor_session in tor_sessions:
    for i in range(THREADS_PER_SESSION):
        worker = Thread(target=scrape, args=(tor_session, q, conn))
        worker.setDaemon(True)
        worker.start()
q.join()
conn.close()
