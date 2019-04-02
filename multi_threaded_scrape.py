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
import logging
from threading import Thread, Lock
from create_tasks_database import create_tasks_database
from datetime import datetime
import sqlite3
from tor_session import DMSession
from dm_map_pages import dm_map_pages


def main():
    THREADS_PER_SESSION = 10
    NUMBER_OF_SESSIONS = 10

    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',
                        filename="scrape.log")

    # create database with links to scrape
    urls = dm_map_pages()
    db_filepath = create_tasks_database(market="dream_market", urls=urls)

    # make unique tor sessions
    dm_sessions = make_unique_tor_sessions(NUMBER_OF_SESSIONS)

    # sign into each session using selenium, pass to requests tor_session object
    for ds in dm_sessions:
        ds.login()

    task_manager = TaskManager(db_filepath=db_filepath)

    # assign x threads per tor_session to begin scraping
    for ds in dm_sessions:
        for i in range(THREADS_PER_SESSION):
            task_manager.start_thread(dm_session=ds)
    task_manager.q.join()
    task_manager.conn.close()


def make_unique_tor_sessions(number_of_sessions):
    tor_sessions = []
    ips = []

    for i in range(number_of_sessions):
        SOCKSPort = 40000 + i
        ControlPort = 41000 + i
        ds = DMSession(SOCKSPort=SOCKSPort, ControlPort=ControlPort)

        # for each session, ensure IP is unique.
        # for duplicates, get new identity
        retries = 0
        max_retries = 5
        while True:
            if ds.ip not in ips:
                tor_sessions.append(ds)
                ips.append(ds.ip)
                break
            elif retries >= max_retries:
                print("Tor session {} was removed after failing to acquire a unique identity".format(i))
                break
            ds.get_new_identity()
            # todo - might not make sense to include logging in here. Revisit
            retries += 1

    return tor_sessions


class TaskManager:
    # requires db_filepath to initialize
    # start_thread and scrape require a TorSession object

    def __init__(self, db_filepath):
        self.lock = Lock()
        logging.debug("Connecting to database: {}".format(db_filepath))
        self.conn = sqlite3.connect(db_filepath, check_same_thread=False)
        logging.debug("Connected to database: {}".format(db_filepath))
        # modifying conn.row_factory modifies how sqlite will return values when running queries.
        # specifically, it forces it to return a list instead of a list of tuples
        self.conn.row_factory = lambda cursor, row: row[0]
        self.c = self.conn.cursor()
        urls = self.c.execute("SELECT url FROM Tasks WHERE completed == 0").fetchall()

        # create queue for multi-threading and fill with urls from db
        self.q = Queue(maxsize=0)
        for i in range(len(urls)):
            self.q.put((i, urls[i]))

    # todo - this may be very inefficient
    # todo - consider saving progress in chunks
    def update_task_database(self, completed, page_text, url):
        logging.debug("Waiting to acquire lock")
        with self.lock:
            logging.debug("Lock acquired")
            self.c.execute("""UPDATE Tasks
                      "SET completed = ?, page_text = ?, scraped_timestamp = ?, 
                       WHERE url = ?""",
                       (completed, page_text, datetime.utcnow(), url))
            self.conn.commit()
        logging.debug("Lock released")

    def start_thread(self, dm_session):
        worker = Thread(target=self.scrape, args=(dm_session, self.q, self.conn))
        worker.setDaemon(True)
        worker.start()

    def scrape(self, dm_session):
        while not self.q.empty():
            work = self.q.get()
            page_text = dm_session.dm_get(work[1]).text
            self.update_task_database(1, page_text, work[1])
            logging.debug("Scraped %s", work[1])
            self.q.task_done()


if __name__ == "__main__":
    main()