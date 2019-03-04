import sqlite3
import os
from datetime import datetime


def create_tasks_database():
    urls = get_urls()

    market = "dream_market"
    date = datetime.now().strftime('%Y_%m_%d')
    filename = "{}_{}.db".format(market, date)

    conn = init_db(filename)
    c = conn.cursor()

    # convert URLs into format that makes it easier to insert all into the database
    # format is (url, completed), where completed = 0 to indicate that the links
    # have not yet been visited/scraped
    data_urls = []
    for url in urls:
        data_urls.append((url, 0))
        
    # insert values into database and close
    c.executemany("INSERT INTO Tasks (url, completed) \
        VALUES (?, ?)", data_urls)
    conn.commit()
    conn.close()
    return os.path.abspath(filename)  # todo confirm this works as expected

    
def init_db(filename):
    assert (not os.path.isfile(filename)), "A database with the name {} already exists".format(filename)

    conn = sqlite3.connect(filename)

    c = conn.cursor()
    # in order to confirm boolean restriction is working correctly
    c.execute('''CREATE TABLE Tasks
        (url TEXT NOT NULL UNIQUE,
        completed BOOLEAN NOT NULL CHECK (completed IN(0,1ctvnews)),
        page_text STRING,
        identified_timestamp DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
        scraped_timestamp DATETIME);''')

    # todo - add a Failures table to keep track of error messages
    return conn
    
    
def get_urls():
    # todo - replace with a function to actually gather a list of URLs for the specified market
    # todo - consider moving the url-gathering to a different file and
    # todo - just have that list of URLs be passed to this file
    urls = [
        "https://www.amazon.ca/",
        "https://tor.stackexchange.com/questions/2006/how-to-run-multiple-tor-browsers-with-different-ips",
        "https://tor.stackexchange.com/questions/6235/how-to-run-multiple-tor-browsers-simultaneously-and-independently-with-different?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/6207/multiple-tor-browser-instances-without-using-vm-sandboxies?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/4725/how-to-run-many-tor-browsers-at-once-all-with-different-ips?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/9364/launch-multiple-sessions-or-instances-on-os-x?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/12436/multiple-ips-with-tor?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/14624/mac-how-to-run-multiple-instances-of-tor-browser-at-the-same-time-with-differen?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/16263/make-same-link-use-different-ip-in-tabs?noredirect=1&lq=1https://tor.stackexchange.com/questions/3606/run-multiple-tor-browsers?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/8643/how-to-run-multiple-tor-browser-5-0-2-how-it-is-different-4-5?noredirect=1&lq=1",
        "https://tor.stackexchange.com/questions/6846/multiple-instances-of-tor-w-tor-browser-since-v4-5?noredirect=1&lq=1",
        "https://stackoverflow.com/questions/18219779/bulk-insert-huge-data-into-sqlite-using-python",
        "https://www.novixys.com/blog/updating-file-multiple-threads-python/",
        "https://www.ctvnews.ca/canada/humboldt-bus-crash-victim-s-father-says-meeting-driver-was-powerful-1.4276982",
        "https://dailyhive.com/vancouver/surrey-shooting-suspect-january-2019",
        "https://www.ctvnews.ca/canada/a-lot-of-hurt-families-humboldt-sentencing-hearing-tough-on-loved-ones-1.4276496",
        "https://www.huffingtonpost.ca/2019/01/31/paris-police-officers-found-guilty-of-gang-raping-canadian-tourist_a_23657919/",
        "https://globalnews.ca/news/4911521/paris-police-rape-canadian-tourist/",
        "https://www.ctvnews.ca/world/police-from-elite-french-unit-found-guilty-in-gang-rape-of-canadian-tourist-1.4277018",
        "https://www.cbc.ca/news/canada/ottawa/ottawa-airport-traffic-tower-control-1.4998246",
        "https://www.narcity.com/news/tim-hortons-unveils-new-double-double-coffee-bars-and-bottled-iced-capps",
        "https://www.cbc.ca/news/business/supreme-court-redwater-decision-orphan-wells-1.4998995",
        "https://www.cbc.ca/news/canada/british-columbia/manhunt-in-surrey-b-c-after-transit-officer-shot-at-skytrain-station-1.4999837",
        "https://globalnews.ca/news/4909321/greens-nanaimo-byelection/",
        "https://globalnews.ca/news/4908979/us-midwest-cold-deaths/",
        "https://globalnews.ca/news/4908853/juan-guaido-venezuela-military-maduro/",
        "https://www.ctvnews.ca/world/trump-appears-to-sour-on-congressional-border-security-talks-1.4276738"
    ]
    return urls
    
# when trying to scrape:
# "https://torontosun.com/news/local-news/warmington-bury-mcarthur-in-at-least-200-years-of-prison-time",
# the program just hung with no error message. Look into why that happened
# when just using "request.get(url)" separately, it loaded it like normal
    
    
if __name__ == "__main__":
    create_tasks_database()