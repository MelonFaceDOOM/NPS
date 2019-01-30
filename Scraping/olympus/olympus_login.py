from bs4 import BeautifulSoup
import base64
import requests


session = requests.Session()

#After Tor is open, direct traffic through the same port
session.proxies = {'http': 'socks5h://127.0.0.1:9150', 'https': 'socks5h://127.0.0.1:9150'}

url = session.get("http://waeixxcraed4gw7q.onion/signin")
soup = BeautifulSoup(url.text, "lxml")
imgs = soup.findAll('img')

#save captcha from base64 encoding (captcha is the 2nd image in the html page; cut first 23 characters out from string to leave base64 img)
img_data = bytes(imgs[1]['src'][23:],encoding='utf-8')
with open("olympus_captcha.jpg","wb") as fh:
    fh.write(base64.decodestring(img_data))

#solve the captcha that has been saved to the harddrive    
captcha = input("enter captcha:\n")

#attempt login (password and username removed)
payload = {"username":username, "password":password, "captcha":captcha}
response = session.post("http://waeixxcraed4gw7q.onion/signin", data = payload)
print(response.text)