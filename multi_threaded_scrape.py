from queue import Queue
import requests
from threading import Thread, Lock
from create_tasks_database import create_tasks_database
from datetime import datetime
import sqlite3

# todo - this may be very inefficient
# todo - consider saving progress in chunks
def mark_task_completed(conn, page_text, url):
    global lck
    lck.acquire()
    c = conn.cursor()
    # todo - add checks to make sure that the URL value is present and that there is only 1 value that is found
    c.execute("UPDATE Tasks SET completed = 1 WHERE url = ?", (url,))
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
        except:
            page_text = ""
        mark_task_completed(conn, page_text, work[1])
        q.task_done()
    return True
    
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
    q.put((i,urls[i]))
    
# start each thread
for i in range(num_threads):
    worker = Thread(target=scrape, args=(q,conn))
    worker.setDaemon(True)
    worker.start()
    
q.join()
conn.close()