'''
Assumes DataDirectory = etc/tor
requires a template file, "torrc_template"
'''

import subprocess
from stem import Signal
from stem.control import Controller
import warnings
from os import path
import base64
from PIL import Image
from io import BytesIO
from selenium import webdriver
import requests
from lxml import html
import re
import sys
import logging


class TorSession(requests.Session):
    # todo - add arguments for password
    # todo - test if CookieAuthentication is necessary
    def __init__(self, SOCKSPort=9050, ControlPort=9051, torrc_dir=None):
        super().__init__()

        if torrc_dir is None:
            torrc_dir = path.relpath("tor/torrc")

        with open("torrc_template", "r") as f:
            torrc_template = f.read()

        with open(torrc_dir, "w") as f:
            f.write(torrc_template.format(
                SOCKSPort=SOCKSPort,
                ControlPort=ControlPort))

        # todo - test to see if provided ports are already in use

        p = subprocess.Popen(["sudo", "./start_tor.sh", torrc_dir], stdout=subprocess.PIPE)  # todo - test
        while True:
            line = p.stdout.readline()
            print(line)
            if b"Bootstrapped 100%" in line:
                print("Finished establishing tor circuit.")
                break
            elif b"Address already in use" in line: # todo - this error means the port is in use. Add step to actually confirm tor is the thing using it
                print("Tor already running.")
                break

        self.proxies = {}
        self.proxies['http'] = 'socks5h://localhost:{}'.format(SOCKSPort)
        self.proxies['https'] = 'socks5h://localhost:{}'.format(SOCKSPort)

        self.ip = self.get("http://httpbin.org/ip").text
        self.SOCKSPort = SOCKSPort
        self.ControlPort = ControlPort

    def get_new_identity(self):
        max_retries = 5
        retries = 0
        while True:
            with Controller.from_port(port=self.ControlPort) as controller:
                controller.authenticate(password="imamelon")
                controller.signal(Signal.NEWNYM)
            super().__init__()  # necessary to get new session object for new ip to work on linux for some reason
            self.proxies = {}
            self.proxies['http'] = 'socks5h://localhost:{}'.format(self.SOCKSPort)
            self.proxies['https'] = 'socks5h://localhost:{}'.format(self.SOCKSPort)
            new_ip = self.get('http://httpbin.org/ip').text
            if new_ip != self.ip:
                self.ip = new_ip
                break
            if retries >= max_retries:
                warnings.warn("Warning: Unable to obtain new identity after {} tries".format(max_retries))
                break
            retries += 1

    def pass_cookies(self, cookies):
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        }
        self.headers.update(headers)
        for cookie in cookies:
            c = {cookie['name']: cookie['value']}
            self.cookies.update(c)


class DMSession(TorSession):
    logging.basicConfig(filename='DMSession.log', filemode='w', level=logging.DEBUG)

    def __init__(self, SOCKSPort=9050, ControlPort=9051, torrc_dir=None):
        if torrc_dir is None:
            torrc_dir = path.relpath("tor/torrc")
        super().__init__(SOCKSPort=SOCKSPort, ControlPort=ControlPort, torrc_dir=torrc_dir)
        self.base_url = ""
        self.username = ""
        self.password = ""
        self.known_errors = [
            "ddos protection",
        ]
        self.logger = logging.getLogger(__name__)

    def get_best_url(self):

        # get alternative links listed on deepdotweb
        ddw_dm_alternative_links = requests.get("https://www.deepdotweb.com/dream-markets-alternative-links/").text
        tree = html.fromstring(ddw_dm_alternative_links)
        link_container = tree.xpath("//div[@class='entry']/ol/li/a")
        links = []
        for link in link_container:
            links.append(link.attrib['href'])

        # Attempt to load each onion page 3 times and measure load times.
        all_load_times = []
        for link in links:
            link_times = {"url": link,
                          "load_times": []}
            for i in range(3):
                load_time = measure_load_time(self, str(link))
                link_times['load_times'].append(load_time)
            all_load_times.append(link_times)

        # format results: (url, number of successful responses, average response time)
        new_list = []
        for l in all_load_times:
            successful_responses = []
            for i in l["load_times"]:
                if type(i) is int or type(i) is float:
                    successful_responses.append(i)
            if len(successful_responses) > 0:
                average = sum(successful_responses) / len(successful_responses)
            else:
                average = "0"
            new_list.append((l['url'], len(successful_responses), average))

        # sort first by number of successful responses, then average response time as a tie-breaker
        sorted_urls = sorted(new_list, key=lambda x: (-x[1], x[2]))
        print(sorted_urls) # temporary test
        best_url = sorted_urls[0][0]

        pattern = "^.+[.]onion"
        base_url = re.match(pattern, best_url)

        self.base_url = base_url
        return base_url

    def login(self, headless=True):
        # Building the profile, setting the port equal to tor on localhost
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", "127.0.0.1")
        profile.set_preference("network.proxy.socks_port", self.SOCKSPort)
        profile.set_preference("network.proxy.socks_remote_dns", True)

        # Tor Browser settings, to bypass fingerprinting
        profile.set_preference("places.history.enabled", False)
        profile.set_preference("privacy.clearOnShutdown.offlineApps", True)
        profile.set_preference("privacy.clearOnShutdown.passwords", True)
        profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
        profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
        profile.set_preference("signon.rememberSignons", False)
        profile.set_preference("network.dns.disablePrefetch", True)
        profile.set_preference("network.http.sendRefererHeader", 0)

        profile.update_preferences()

        # Setting the binary path for firefox

        # make browser headless
        options = webdriver.FirefoxOptions()
        options.headless = headless

        driver = webdriver.Firefox(firefox_profile=profile, options=options)

        if not self.base_url:
            print("no base url found, attempting to get link from ddw. May take a few minutes as each is tested.")
            self.get_best_url()

        while True:
            driver.get(self.base_url)

            # find the captcha element
            ele_captcha = driver.find_element_by_xpath("//img[@alt='Captcha']")

            # get the captcha as a base64 string
            img_captcha_base64 = driver.execute_async_script("""
                var ele = arguments[0], callback = arguments[1];
                ele.addEventListener('load', function fn(){
                  ele.removeEventListener('load', fn, false);
                  var cnv = document.createElement('canvas');
                  cnv.width = this.width; cnv.height = this.height;
                  cnv.getContext('2d').drawImage(this, 0, 0);
                  callback(cnv.toDataURL('image/jpeg').substring(22));
                }, false);
                ele.dispatchEvent(new Event('load'));
                """, ele_captcha)

            # Open image and have user input answer
            im = Image.open(BytesIO(base64.b64decode(img_captcha_base64)))
            im.show()
            captcha_text = input("Please enter captcha text")
            driver.find_element_by_xpath("//input[@title='Captcha, case sensitive']").send_keys(captcha_text)

            # Enter the username
            input_element = driver.find_elements_by_xpath(
                "//input[@value='' or @value='{}' and @type='text']".format(
                    self.username))[0]
            input_element.clear()  # Clear field because if captcha failed the username will still remain
            input_element.send_keys(self.username)
            # Enter the password
            input_element = driver.find_elements_by_xpath("//input[@value='' and @type='password']")[0]
            input_element.send_keys(self.password)

            # Submit the form
            driver.find_element_by_xpath("//input[@value='Login']").click()

            try:
                driver.find_element_by_xpath(
                    "//div[contains(@class, 'title') and text()='Login with existing user']")
                # still on login page, try again
            except:
                break  # captcha did not fail. Quit loop

        return driver.get_cookies()

    def dm_get(self, url):
        # todo - make sure url is in the same domain as self.base_url

        max_retries = 5
        retries = 0
        while True:
            # first, check to see if get(url) works successfully
            self.logger.debug("trying to get url: %s", url)
            try:
                page = self.get(url)
                self.logger.debug("successfully reached url: %s", url)
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries < max_retries:

                    self.logger.info("getting new identity after failing to get url", exc_info=True)
                    self.get_new_identity()
                    self.login()
                    # todo - consider getting a new mirror (especially for timeout error)
                else:
                    self.logger.info("max retries reached; failed to reach url", exc_info=True)
                    print(e)  # todo - temporary
                    sys.exit()  # todo - temporary
                    return e

            # second, confirm that we reached the intended page, and not an error page
            page_errors = [known_error for known_error in self.known_errors if known_error in page.text]
            if len(page_errors) > 0:
                for error in page_errors:
                    self.logger.info("error page reached (%s) when trying to access url: %s", error, url)
                retries += 1
                if retries < max_retries:
                    self.logger.info("getting new identity after failing to get url", exc_info=True)
                    self.get_new_identity()
                    self.login()
                else:
                    self.logger.debug("max retries reached; failed to reach url", exc_info=True)
                    sys.exit()
            else:
                return page


class WSMSession(TorSession):
    logging.basicConfig(filename='WSMSession.log', filemode='w', level=logging.DEBUG)

    def __init__(self, SOCKSPort=9050, ControlPort=9051, torrc_dir=None):
        if torrc_dir is None:
            torrc_dir = path.relpath("tor/torrc")
        super().__init__(SOCKSPort=SOCKSPort, ControlPort=ControlPort, torrc_dir=torrc_dir)
        self.base_url = ""
        self.username = ""
        self.password = ""
        self.token = ""
        self.known_errors = [
            "ddos protection",
        ]
        self.logger = logging.getLogger(__name__)

    def complete_security_check(self, content, base_url):

        tree = html.fromstring(content.text)
        while self.security_check_page(tree):
            token = tree.xpath("//input[@id='form__token']")[0].get("value")
            if self.token != token:
                self.token = token

            # get src, truncate leading text, convert b64 to image and open
            captcha_b64 = tree.xpath("//img [@class='captcha_image']")[0].get("src")[23:]
            im = Image.open(BytesIO(base64.b64decode(captcha_b64)))
            im.show()
            captcha_text = input("Please enter captcha text")

            payload = {
                'form[_token]': self.token,
                'form[captcha]': captcha_text
            }

            headers = {
                'Host': base_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'http://{}'.format(base_url),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '84',
                'Cookie': 'PHPSESSID={}'.format(self.cookies['PHPSESSID']),
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            content = self.post(url='http://{}'.format(base_url), data=payload, headers=headers)
            tree = html.fromstring(content.text)
        return content

    def complete_login(self, content, base_url):

        tree = html.fromstring(content.text)
        while self.login_page(tree):
            token = tree.xpath("//input[@id='form__token']")[0].get("value")
            if self.token != token:
                self.token = token

            #get src, truncate leading text, convert b64 to image and open
            captcha_b64 = tree.xpath("//img [@class='captcha_image']")[0].get("src")[23:]
            im = Image.open(BytesIO(base64.b64decode(captcha_b64)))
            im.show()
            captcha_text = input("Please enter captcha text")

            payload = {
                'form[_token]': token,
                'form[captcha]': captcha_text,
                'form[extendForm]': 'on',
                'form[language]': 'en',
                'form[password]': self.password,
                'form[pictureQuality]': '0',
                'form[sessionLength]': '43200',
                'form[username]': self.username
            }

            headers = {
                'Host': base_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'http://{}/login'.format(base_url),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '238',
                'Cookie': 'PHPSESSID={}'.format(self.cookies['PHPSESSID']),
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            content = self.post(url='http://{}/login'.format(base_url), data=payload, headers=headers)
            tree = html.fromstring(content.text)

        return content

    def create_account(self, tree, base_url):
        # todo - add random username/password
        username = ""
        password = ""

        token = tree.xpath("//input[@name='token']")[0].get("value")
        if self.token != token:
            self.token = token

        cid = tree.xpath("//input[@name='cid']")[0].get("value")
        # get src, truncate leading text, convert b64 to image and open
        captcha_b64 = tree.xpath("//div [@class='wms_captcha_field]/img")[0].get("src")[
                      23:]  # todo - needs to be tested
        # captcha_b64 = tree.xpath("//img [@class='captcha_image']")[0].get("src")[23:]
        im = Image.open(BytesIO(base64.b64decode(captcha_b64)))
        im.show()
        captcha_text = input("Please enter captcha text")

        payload = {
            'captcha': 'HJnWc',
            'cid': cid,
            'password': password,
            'passwordrep': password,
            'token': token,
            'tokenid': '4',
            'tokentime': '1554146183',
            'username': username
        }

        headers = {
            'Host': base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://{}/signup?ref=276'.format(base_url),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '162',
            'Cookie': 'PHPSESSID={}'.format(self.cookies['PHPSESSID']),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # todo -- if successful, add username and password to self
        return self.post(url='http://{}/signup?ref=276'.format(base_url), data=payload, headers=headers)

    def security_check_page(self, tree):
        return bool(tree.xpath(".// h3[text()='Security Check']"))

    def login_page(self, tree):
        return bool(tree.xpath(".// h3[text()='Log In']"))

    def login(self):
        content = self.get("http://{}/login".format(self.base_url))

        # todo - add contigencies for returning back to pre-login screen or receiving a 404 response
        while True:
            tree = html.fromstring(content.text)
            if self.security_check_page(tree):
                print('trying to complete security check')
                content = self.complete_security_check(content, self.base_url)
                print('security check completed')
            elif self.login_page(tree):
                print('trying to complete login')
                content = self.complete_login(content, self.base_url)
                print('login completed')
                return content
            else:
                print("unknown page reached")
                sys.exit()

    def get_wsm_page(self, headers, catT="", catM="", catB="", menuCatM="", menuCatB="", page="1"):
        payload = {
            'form[_token]': self.token,
            'form[catT]': catT,
            'form[catM]': catM,
            'form[catB]': catB,
            'form[searchTerm]': "",
            'form[limit]': "15",
            'form[rating]': "0",
            'form[vendorLevel]': "1",
            'form[vendoractivity]': "0",
            'form[quantity]': "0",
            'form[maxpricepunit]': "0",
            'form[shipsfrom]': "0",
            'form[shipsto]': "0",
            'form[page]': page,
            'form[sort]': "pop_week_desc",
            'menuCatM': menuCatM,
            'menuCatB': menuCatB
        }
        content = self.post(url="https://{}/index".format(self.base_url), headers=headers, data=payload)
        tree = html.fromstring(content.text)
        for title in tree.xpath("//h4[@class='card-title']/a"):
            print(title.text)
        return content


def measure_load_time(tor_session, url):
    try:
        load_time = tor_session.get(url, timeout=15).elapsed.total_seconds()
    except:
        load_time = "failed to load"
    return load_time