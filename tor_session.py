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
            new_ip = self.get('http://httpbin.org/ip').text
            if new_ip != self.ip:
                self.ip = new_ip
            if retries >= max_retries:
                warnings.warn("Warning: Unable to obtain new identity after {} tries".format(max_retries))
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


class DmSession(TorSession):
    logging.basicConfig(filename='DmSession.log', filemode='w', level=logging.DEBUG)

    def __init__(self, SOCKSPort=9050, ControlPort=9051, torrc_dir=None):
        if torrc_dir is None:
            torrc_dir = path.relpath("tor/torrc")
        super().__init__(SOCKSPort=SOCKSPort, ControlPort=ControlPort, torrc_dir=torrc_dir)
        self.base_url = ""
        self.username = ""
        self.password = ""
        self.known_errors = [
            "ddos protection",
            "captcha"
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


def measure_load_time(tor_session, url):
    try:
        load_time = tor_session.get(url, timeout=15).elapsed.total_seconds()
    except:
        load_time = "failed to load"
    return load_time