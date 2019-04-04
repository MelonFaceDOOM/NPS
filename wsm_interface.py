# from dm_map_pages import dm_map_pages
#
# dm_list = dm_map_pages()
#
# with open("dm_mapped_pages.txt","w") as f:
#     for item in dm_list:
#         f.write("%s\n" % item)


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

while True:
    command = input("enter command")

    if command == "run":

        with open('wsm_input.txt', 'r') as file:
             wsm_dict = json.load(file)

        try:
            content = ws.get_wsm_page(headers=headers,catT=wsm_dict['catT'],catM=wsm_dict['catM'],catB=wsm_dict['catB'],
                             menuCatM=wsm_dict['menuCatM'], menuCatB=wsm_dict['menuCatB'], page=wsm_dict['page'])

            if content.status_code == 200:
                tree = html.fromstring(content.text)
                for title in tree.xpath("//h4[@class='card-title']/a"):
                    print(title.text)
            elif content.status_code == 400:
                print("bad request, try again")
            elif content.status_code == 404:
                print("404, trying to re-login...")
                ws.login()

        except requests.exceptions.RequestException as e:
            print(e)
            print("try again?")

    elif command == "index":
        try:
            content = ws.get("http://{}/index".format(ws.base_url))

            if content.status_code == 200:
                tree = html.fromstring(content.text)
                if ws.login_page(tree) or ws.security_check_page(tree):
                    print("logged out")
                else:
                    print("successfully loaded index page")
            elif content.status_code == 400:
                print("bad request, try again")
            elif content.status_code == 404:
                print("404, trying to re-login...")
                ws.login()

        except requests.exceptions.RequestException as e:
            print(e)
            print("try again?")

    elif command in ("quit", "exit"):
        sys.exit()

    elif command == "login":
        ws.login()

    else:
        print("command unknown. try again")
