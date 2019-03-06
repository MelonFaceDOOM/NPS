from wsm_login import wsm_login

username="odrs"
password="odrs123"
port=9150
url="http://wallst3gi4a5wtn4.onion/login"

cookies=wsm_login(username=username,password=password,url=url,port=port)

import requests
from lxml import html
session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9150'
session.proxies['https'] = 'socks5h://localhost:9150'
headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}
session.headers.update(headers)
for cookie in cookies:
    c = {cookie['name']: cookie['value']}
    session.cookies.update(c)
    session.get("http://wallst3gi4a5wtn4.onion/index")

page_content = session.get(url)
tree = html.fromstrong(page_content.text)
token = tree.xpath("//input[@id='form__token']").get("value")
print(token)

page_content = session.get(url)
tree = html.fromstrong(page_content.text)
drugs_button = tree.xpath("//button[@name='menuCatT' and contains(text(),'Drugs')]")


# check current page number by looking for li with class = "page-item active"
#     get li/button text
# wait until element h2 with text = "Products"
# for each div with class = "card"
#     get div/a

# find button with class = "page-link"
# if parent li class ="page-item disabled", then you are on the last page
# if not, click button

# form[_token]=0PXpyrEwuEjMVSeiVqrWrG3NGGpEzgZvex_dROTSBuY
# form[catT]=1
# form[catM]=0
# form[catB]=0
# form[searchTerm]
# form[limit]=15
# form[rating]=0
# form[vendorLevel]=1
# form[vendoractivity]=0
# form[quantity]=0
# form[maxpricepunit]=0
# form[shipsfrom]=0
# form[shipsto]=0
# form[sort]=pop_week_desc
# form[page]=2


# form[_token]=0PXpyrEwuEjMVSeiVqrWrG3NGGpEzgZvex_dROTSBuY
# form[catT]=1
# form[catM]=0
# form[catB]=0
# form[searchTerm]
# form[limit]=15
# form[rating]=0
# form[vendorLevel]=1
# form[vendoractivity]=0
# form[quantity]=0
# form[maxpricepunit]=0
# form[shipsfrom]=0
# form[shipsto]=0
# form[sort]=pop_week_desc
# form[page]=2