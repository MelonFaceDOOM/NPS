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
from tor_session import DmSession


def dm_map_pages():
    ds = DmSession()
    ds.base_url = "http://t3e6ly3uoif4zcw2.onion"
    ds.username = "odrs"
    ds.password = "odrs"
    ds.login()

    page_content = ds.dm_get("{}/?category=104".format(ds.base_url))
    tree = html.fromstring(page_content.text)

    drug_categories = tree.xpath("//div[@class='category  depth1']/a")
    urls_with_page_count = []
    for d in drug_categories:
        cat_url = requests.compat.urljoin(ds.base_url, d.attrib['href'])

        subtree = html.fromstring(ds.dm_get(cat_url).text)

        sub_cats = subtree.xpath("//div[@class='category  depth2']/a")
        if len(sub_cats) > 0:
            for s in sub_cats:
                sub_cat_url = requests.compat.urljoin(ds.base_url, s.attrib['href'])
                subtree = html.fromstring(ds.dm_get(sub_cat_url).text)
                page_count = count_pages(subtree)
                print("{} pages found in category {}".format(page_count, sub_cat_url))
                urls_with_page_count.append((sub_cat_url, page_count))
        else:
            page_count = count_pages(subtree)
            print("{} pages found in category {}".format(page_count, sub_cat_url))
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
    dm_map_pages()
