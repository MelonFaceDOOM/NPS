import requests
from lxml import html
from tor_session import TorSession


def get_best_dm_link():
    
    # get alternative links listed on deepdotweb 
    ddw_dm_alternative_links = requests.get("https://www.deepdotweb.com/wall-st-market-alternative-links/").text
    tree = html.fromstring(ddw_dm_alternative_links)
    link_container = tree.xpath("//div[@class='entry']/ol/li/a")
    links = []
    for link in link_container:
        links.append(link.attrib['href'])
        
    # establish tor session
    tor_session = TorSession

    # Attempt to load each onion page 3 times and measure load times.
    all_load_times = []
    for link in links:
        link_times = {"url": link,
                      "load_times": []}
        for i in range(3):
            load_time = measure_load_time(tor_session, str(link))
            link_times['load_times'].append(load_time)
        all_load_times.append(link_times)
    
    # format results: (url, number of successful responses, average response time)
    new_list = []
    for l in all_load_times:
        successful_responses = []
        for i in l["load_times"]:
            if type(i) is int or type(i) is float:
                successful_responses.append(i)
        if len(successful_responses)> 0:
            average = sum(successful_responses)/len(successful_responses)
        else:
            average = "0"
        new_list.append((l['url'],len(successful_responses),average))
        
    # sort first by number of successful responses, then average response time as a tie-breaker
    sorted_urls = sorted(new_list, key=lambda x: (-x[1],x[2]))
    best_url = sorted_urls[0][0]

    return best_url


def measure_load_time(tor_session, url):
    try:
        load_time = tor_session.get(url, timeout=15).elapsed.total_seconds()
    except:
        load_time = "failed to load"
    return load_time


if __name__ == "__main__":
    get_best_dm_link()