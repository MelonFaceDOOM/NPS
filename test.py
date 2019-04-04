from tor_session import WSMSession
import json
import sys
from lxml import html
import requests

ws = WSMSession()
ws.base_url = "wallst4qihu6lvsa.onion"
ws.username = "odrs"
ws.password = "odrs123"
ws.get_new_identity()
ws.login()

headers = {}
headers['Connection'] = "keep-alive"
headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"
headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
headers['Accept-Language'] = "en-US,en;q=0.5"
headers['Accept-Encoding'] = "gzip, deflate"
headers['Referer'] = ws.base_url
headers['Content-Type'] = "application/x-www-form-urlencoded"
headers['Content-Length'] = "315"
headers['Upgrade-Insecure-Requests'] = "1"
headers['PHPSESSID'] = ws.cookies['PHPSESSID']

with open('wsm_input.txt', 'r') as file:
    wsm_dict = json.load(file)

for key in wsm_dict:
    m, b = wsm_dict[key]

    try:
        content = ws.get_wsm_page(headers=headers, menuCatM=m, menuCatB=b)

        if content.status_code == 200:
            tree = html.fromstring(content.text)
            titles = []
            for title in tree.xpath("//h4[@class='card-title']/a"):
                titles.append(title)
            with open("wsm_drug_front_pages.txt", "a") as f:
                f.write(key+"\n")
                for title in titles:
                    f.write(title+"\n")
                f.write("\n"+"-"*50+"\n\n")
        elif content.status_code == 400:
            with open("wsm_drug_front_pages.txt", "a") as f:
                f.write(key + "\n")
                f.write("error 400 -- bad request")
                f.write("\n" + "-" * 50 + "\n\n")
        elif content.status_code == 404:
            print("404, quitting...")
            sys.exit()
    except requests.exceptions.RequestException as e:
        with open("wsm_drug_front_pages.txt", "a") as f:
            f.write(key + "\n")
            f.write("error:\n")
            f.write(e)
            f.write("\n" + "-" * 50 + "\n\n")