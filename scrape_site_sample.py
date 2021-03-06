'''
This is not a functioning program yet, it was 
just helpful for me to envision the structure
of the program by putting together some
of the basics here. See multi_threaded_scrape.py for
the latest functioning queue/scraping script
'''

import requests
import stem.process
from queue import Queue
from threading import Thread, Lock

# create 10 Tor Clients
ports = [('905' + str(i), '906' + str(i)) for i in range(10)]
HashedControlPassword = "16:C6E1C9BA080F241A604855E33B8105F1884DB32BFB102B8EF766EFEF33"
tor_configs = [{'SOCKSPort': p[0], 'ControlPort': p[1], 'DataDirectory': './tordata' + p[0],
    'HashedControlPassword': '16:A621C9B2020F2402602825E3AB9105F1824DB32B2B102B2EF786EFEF33' 
    } for p in ports]

sessions = []
for cfg in tor_configs:
    stem.process.launch_tor_with_config(config = cfg)
    session = requests.session()
    session.proxies = {}
    port = cfg['SOCKSPort']
    session.proxies['http'] = 'socks5h://localhost:{}'.format(port)
    session.proxies['https'] = 'socks5h://localhost:{}'.format(port)
    sessions.append(session)

# Creating the Task database will be handled separately.
# It will have to be site-specific. The methodology by which the
# database of links is generated will vary greatly based on the structure of each site-specific

task_database = "" # location of database. Alternatively, the database could be passed to this program as an argument
# This could also just be a list of urls

utls = # values in database where completed = False

# It doesn't make sense to fetch batches of urls, becuase then you are waiting
# for the slowest thread to finished before you go and get the next batch.
# Instead, get all urls and add all to queue.

for tor_client in tor_clients:
    scraper = Scraper(tor_client=tor_client)
    url = task.get_task
    scraper.scrape(url)
    
q = Queue(maxsize=0)
num_threads = min(50, len(urls))
results = [{} for x in urls]

for i in range(len(urls)):
    q.put((i,urls[i]))
    
# need to replace the simple "session.get" commands with a full Scraper Class
# Then I need to add functionality like:
    # signing in
    # getting a new identity
    # responding to 404
    
lck = Lock()

def mark_task_completed(url):
    global lck
    lck.acquire()
    #update row associated with task in database to mark that it has been completed
    #commit
    lck.release()
    
def scrape(q, session, result):
    while not q.empty():
        work = q.get()
        try:
            data = session.get(work[1]).text
            result[work[0]] = data
        except:
            result[work[0]] = {}
            
        mark_task_complete(work[1])
        q.task_done()
    return True
    
for i in range(num_threads):
    session = sessions[i]
    worker = Thread(target=scrape, args=(q, session, results))
    worker.setDaemon(True)
    worker.start()
    
# join() pauses the calling thread until the thread in question has finished processing.
# This prevents the program from progressing until all URLs have been processed.
q.join()

for result in results:
    print(result)