import requests
from bs4 import BeautifulSoup
import base64
import time
import os

def download_image_file(url, filename):
    print("Downloading {} ---> {}".format(url, filename))
    # NOTE the stream=True parameter
    r = session.get(url, stream=True)
    with open(r"captchas/"+filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                
def base_64_to_img(b64_string):
    imgdata = base64.b64decode(b64_string[68:])
    return imgdata

def get_image_link(url):
    source_code = session.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    
    for link in soup.findAll('img', {"class": "captcha_image"}):
        image_link = link.get('src')
        if not image_link.startswith('http'):
            image_link = url + '/' + image_link
        return image_link        
        
session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'

DIR = "captchas"

current_captcha_count = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

for i in range(current_captcha_count+1,10000):
    filename = "cap_"+str(i)+".jpg"
    
    try:
        b64_string = get_image_link('http://wallstyizjhkrvmj.onion/signup?ref=276')
    except ConnectionError:
        print("retrying connection in 10 seconds")
        time.sleep(10)
        b64_string = get_image_link('http://wallstyizjhkrvmj.onion/signup?ref=276')
        print("reconnection successful")
    
    
    with open(r"captchas/"+filename, 'wb') as f:
        f.write(base_64_to_img(b64_string))
    
    