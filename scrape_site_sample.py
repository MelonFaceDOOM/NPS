import requests
import stem.process
from queue import Queue
from threading import Thread

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

task_database = "" #location of database. Alternatively, the database could be passed to this program as an argument
#This could also just be a list of urls

# It doesn't make sense to fetch a batches of urls, becuase then you are waiting
# for the slowest thread to finished before you go and get the next batch.
# Instead, get all urls and add all to queue.
# Create a separate list or db of completed urls that is updated as urls as scraped
# The very first step in this program could be to compare the two lists and remove anything
# from the completed list from the list of urls to scrape

for tor_client in tor_clients:
    scraper = Scraper(tor_client=tor_client)
    url = task.get_task
    scraper.scrape(url)
    
q = Queue(maxsize=0)
num_threads = min(10, len(urls))
results = [{} for x in urls]

for i in range(len(urls)):
    q.put((i,urls[i]))
    
# need to replace the simple "session.get" commands with a full Scraper Class
# Then I need to add functionality like:
    # signing in
    # getting a new identity
    # responding to 404
    
def scrape(q, session, result):
    while not q.empty():
        work = q.get()
        try:
            data = session.get(work[1]).text
            result[work[0]] = data
        except:
            result[work[0]] = {}
            
        with open("completed_urls.txt") as f:
            f.write(work[1]+"\n")
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