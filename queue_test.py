from queue import Queue
import requests
from threading import Thread



urls = [
    "https://www.reddit.com/",
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
    "https://tor.stackexchange.com/questions/6846/multiple-instances-of-tor-w-tor-browser-since-v4-5?noredirect=1&lq=1"
]

q = Queue(maxsize=0)
num_threads = min(50, len(urls))
results = [{} for x in urls]

for i in range(len(urls)):
    q.put((i,urls[i]))
    
def crawl(q, result):
    while not q.empty():
        work = q.get()
        try:
            data = requests.get(work[1]).text
            result[work[0]] = data
        except:
            result[work[0]] = {}
        q.task_done()
    return True
    
for i in range(num_threads):
    worker = Thread(target=crawl, args=(q,results))
    worker.setDaemon(True)
    worker.start()
    
q.join()

for result in results:
    print(result)