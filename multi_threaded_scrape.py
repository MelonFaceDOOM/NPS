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
import logging
from threading import Thread, Lock
from create_tasks_database import create_tasks_database
from datetime import datetime
import sqlite3
import os
from tor_session import TorSession
from dm_login import dm_login
from get_best_dm_link import get_best_dm_link


def main():
    THREADS_PER_SESSION = 10
    NUMBER_OF_SESSIONS = 10
    USERNAME = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned
    PASSWORD = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned
    # KNOWN_ERRORS is a list of strings that, if found in a page, indicates a known error page
    KNOWN_ERRORS = ["ddos protection"]
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)

    login_url = get_best_dm_link()
    # login_url = "http://lchudifyeqm4ldjj.onion/?ai=1675"

    # create database with links to scrape
    db_filepath = create_tasks_database()

    # make unique tor sessions
    tor_sessions = make_unique_tor_sessions(NUMBER_OF_SESSIONS,
                                            login_url=login_url,
                                            username=USERNAME,
                                            password=PASSWORD)

    # sign into each session using selenium, pass to requests tor_session object
    for tor_session in tor_sessions:
        # todo - test this: it's possible that selenium auto-closing after logging in
        # todo - might make the cookies not suffice when passed to the requests session
        cookies = dm_login(login_url, USERNAME, PASSWORD, tor_session.SOCKSPort)
        tor_session.pass_cookies(cookies)

    task_manager = TaskManager(login_url=login_url,
                               username=USERNAME,
                               password=PASSWORD,
                               known_errors=KNOWN_ERRORS,
                               db_filepath=db_filepath)

    # assign x threads per tor_session to begin scraping
    for tor_session in tor_sessions:
        for i in range(THREADS_PER_SESSION):
            task_manager.start_thread(tor_session=tor_session)
    task_manager.q.join()
    task_manager.conn.close()


def make_unique_tor_sessions(number_of_sessions, login_url, username, password, tor_dir="etc/tor/"):
    tor_sessions = []
    ips = []

    for i in range(number_of_sessions):

        SOCKSPort = 40000 + i
        ControlPort = 41000 + i

        torrc_dir = os.path.join(tor_dir, "torrc.{}".format(i))

        tor_session = TorSession(SOCKSPort=SOCKSPort,
                                 ControlPort=ControlPort,
                                 torrc_dir=torrc_dir)

        # for each session, ensure IP is unique.
        # for duplicates, get new identity
        retries = 0
        max_retries = 5
        while True:
            if tor_session.ip not in ips:
                tor_sessions.append(tor_session)
                ips.append(tor_session.ip)
                break
            elif retries >= max_retries:
                print("Tor session {} was removed after failing to acquire a unique identity".format(i))
                break
            tor_session.get_new_identity()
            dm_login(login_url, username, password, tor_session.SOCKSPort)
            retries += 1

    return tor_sessions


class TaskManager:
    # requires db_filepath to initialize
    # start_thread and scrape require a TorSession object

    def __init__(self, login_url, username, password, known_errors, db_filepath):
        self.lock = Lock()
        self.login_url = login_url
        self.username = username
        self.password = password
        self.known_errors = known_errors
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

    def start_thread(self, tor_session):
        worker = Thread(target=self.scrape, args=(tor_session, self.q, self.conn))
        worker.setDaemon(True)
        worker.start()

    def scrape(self, tor_session):

        while not self.q.empty():
            work = self.q.get()
            try:
                page_text = tor_session.get(work[1]).text
            except requests.exceptions.RequestException as e:
                page_text = e  # todo - add different procedures depending on error
                               # todo - probably want to get new identity after a timeout, but not a 404
                logging.debug("tried to scrape {} but encountered the following exception: \n {}".format(work[1], e))

            # make sure page loaded correctly before marking as completed
            page_error = [known_error for known_error in self.known_errors if known_error in page_text]
            if page_error > 0:
                logging.debug("Tried to scrape {} but encountered error: ".format(work[1], page_error))
                # todo - may be a good idea to add a with self.lock statement for the new identity/logging in
                tor_session.get_new_identity()
                dm_login(self.login_url, self.username, self.password, tor_session.SOCKSPort)
            else:
                self.update_task_database(1, page_text, work[1])
                logging.debug("Successfully scraped {}".format(work[1]))
            self.q.task_done()


if __name__ == "__main__":
    main()