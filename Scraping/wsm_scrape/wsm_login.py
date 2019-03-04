#requires Tor to be open to establish the connection

import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
from io import BytesIO

#establish session through already-opened port
session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'

#access website
plain_text = session.get('http://wallst3gi4a5wtn4.onion/signup?ref=276').text
soup = BeautifulSoup(plain_text, "html.parser")
    
image_b64 = soup.find('img', {"class": "captcha_image"})
image_b64 = image_b64.get('src')

imgdata = base64.b64decode(image_b64[23:])

img = Image.open(BytesIO(imgdata))
img.show()