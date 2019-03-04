from wsm_login import wsm_login

import requests
import re
import time
from lxml import html
#from wsm_login import wsm_login

session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'

cookies = wsm_login(url="http://wallst3gi4a5wtn4.onion/login", username="odrs", password="odrs123", port=9150)

headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}
session.headers.update(headers)
for cookie in cookies:
    c = {cookie['name']: cookie['value']}
    session.cookies.update(c)
    
page_text = session.get("http://wallst3gi4a5wtn4.onion/index").text

with open("out_file.txt", "w") as f:
    f.write(page_text)