# Tor browser must be open before running this script
'''
1) go through drug categories on Dream Market
2) map contents (i.e. sub-category URLs, number of pages in each category
3) erase the current contents of the "scrape_progress" file
4) save a list of URLs to be scraped in "scrape_progress"
'''

import re
from lxml import html
import requests
from tor_session import TorSession
from dm_login import dm_login


def main():
    URL = "7ep7acrkunzdcw3l.onion"
    USERNAME = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned
    PASSWORD = "odrs"  # Todo - get username and password from a pool that keeps track of where they are banned

    tor_session = TorSession()
    cookies = dm_login(url=URL, username=USERNAME, password=PASSWORD, port=tor_session.SOCKSPort)
    tor_session.pass_cookies(cookies=cookies)

    page_content = tor_session.get("{}/?category=104".format(URL))
    tree = html.fromstring(page_content.text)

    drug_categories = tree.xpath("//div[@class='category  depth1']/a")
    urls_with_page_count = []
    for d in drug_categories:
        cat_url = requests.compat.urljoin(URL, d.attrib['href'])
        subtree = html.fromstring(tor_session.get(cat_url).text)
        sub_cats = subtree.xpath("//div[@class='category  depth2']/a")
        if len(sub_cats) > 0:
            for s in sub_cats:
                sub_cat_url = requests.compat.urljoin(URL, s.attrib['href'])
                subtree = html.fromstring(tor_session.get(sub_cat_url).text)
                page_count = count_pages(subtree)
                urls_with_page_count.append((sub_cat_url, page_count))
        else:
            page_count = count_pages(subtree)
            urls_with_page_count.append((cat_url, page_count))

    all_urls = []
    for url, page_count in urls_with_page_count:
        urls = gen_url_list(url, page_count)
        all_urls += urls

    return all_urls


def count_pages(tree):
    try:
        pages = tree.xpath("//ul[@class='pageNav']/li/a")
        page_count = int(pages[-2].text)  # the last page will be the 2nd last li element
    except:  # there will be no pageNav if there is only 1 page in this category
        page_count = 1

    return page_count


def gen_url_list(url, num_pages):
    reg_pattern = "category=([0-9]+)"
    category = re.search(reg_pattern, url).groups(1)[0]
    urls = []
    [urls.append("/?page={page}&category={category}".format(page=page, category=category))
     for page in range(1, num_pages + 1)
     ]

    return urls


if __name__ == "__main__":
    main()
