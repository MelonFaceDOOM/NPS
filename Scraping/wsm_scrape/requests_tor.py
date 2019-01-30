import requests
#from bs4 import BeautifulSoup
#requires Tor to be open to establish the connection

session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'
r = session.get('http://wallstyizjhkrvmj.onion/login')
c = r.text
with open("wsm_login.txt", 'w') as f:
    f.write(c)