#Tor browser must be open before running this script
'''
1) go through drug categories on Dream Market
2) map contents (i.e. sub-category URLs, number of pages in each category
3) erase the current contents of the "scrape_progress" file
4) save a list of URLs to be scraped in "scrape_progress"
'''
import re
import time
from lxml import html

from tor_session import TorSession
from dm_login import dm_login


URL = "7ep7acrkunzdcw3l.onion"
USERNAME = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned
PASSWORD = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned

tor_session = TorSession
cookies = dm_login(url=URL, username=USERNAME, password=PASSWORD, port=tor_session.SOCKSPort)
tor_session.pass_cookies(cookies)

page_content = tor_session.get("{}/?category=104".format(URL))
tree = html.fromstring(page_content)

drug_categories = tree.xpath("//div[@class='category  depth1']/a")


def main():

    #######################
    ### MAP SITE LAYOUT ###
    #######################
    
    driver.get("{}/?category=104".format(dm_mirror))
    
    #"{domain}/?page={page}&category={category}".format(domain=domain,page=page,category=category)

    #create a list of all URLs to be scraped
    to_scrape = []

    drug_cats = driver.find_elements_by_xpath("//div[@class='category  depth1']/a")
    cat_urls = []
    for drug_cat in drug_cats:
        cat_urls.append(drug_cat.get_attribute("href"))

    for url in cat_urls:
        driver.get(url)

        sub_cat_urls = []
        for element in driver.find_elements_by_xpath("//div[contains(@class, 'category  depth2')]/a"):
            sub_cat_urls.append(element.get_attribute("href"))
            
        if len(sub_cat_urls) == 0:
            num_pages = count_pages(driver)
            to_scrape.extend(gen_url_list(num_pages,url))
            
        else:
            for sub_cat_url in sub_cat_urls:
                driver.get(sub_cat_url)
                num_pages = count_pages(driver)
                to_scrape.extend(gen_url_list(num_pages,sub_cat_url))
        
        time.sleep(5)  # attempt to avoid ddos protection
        
        
    with open("scrape_progress", "wb") as sp:
        pickle.dump(to_scrape,sp)
    
def count_pages(driver):
    try:
        pageNav = driver.find_element_by_xpath("//ul[@class='pageNav']")
        pages = pageNav.find_elements_by_tag_name("li")
        page_count = int(pages[-2].text) #the last page will be the 2nd last li element
    except: # there will be no pageNav if there is only 1 page in this category
        page_count = 1
        
    return page_count
        
def gen_url_list(num_pages,url):
    reg_pattern = "category=([0-9]+)"
    category = re.search(reg_pattern,url).groups(1)[0]
    urls =[]
    [urls.append("/?page={page}&category={category}".format(page=page,category=category))
     for page in range(1,num_pages+1)
    ]
    
    return urls
            
if __name__ == "__main__":
    main()