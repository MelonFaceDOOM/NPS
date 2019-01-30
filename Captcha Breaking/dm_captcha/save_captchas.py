import requests
from bs4 import BeautifulSoup

def download_file(url, filename):
    print("Downloading {} ---> {}".format(url, filename))
    # NOTE the stream=True parameter
    r = session.get(url, stream=True)
    with open(r"captchas/"+filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def Download_Image_from_Web(url,filename):
    source_code = session.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    
    for link in soup.findAll('img', {"class": "captcha3"}):
        image_links = link.get('src')
        if not image_links.startswith('http'):
            image_links = url + '/' + image_links
        download_file(image_links, filename)
        
        
session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'

for i in range(9000,10000):
    filename = "cap_"+str(i)+".png"
    Download_Image_from_Web('http://lchudifyeqm4ldjj.onion/',filename)