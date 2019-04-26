import requests

url = "https://www.rechem.ca/index.php?route=product/product&product_id=515"

headers = {
    'authority': 'www.rechem.ca',
    'method': 'GET',
    'path': '/index.php?route=product/product&product_id=515',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;'
              'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.rechem.ca/index.php?route=information/contact',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
}


r = requests.get(url, headers=headers)
print(r.text)