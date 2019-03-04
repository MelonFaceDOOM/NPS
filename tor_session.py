'''
Assumes DataDirectory = etc/tor
requires a template file, "torrc_template"
'''

import os
import subprocess
from stem import Signal
from stem.control import Controller
import requests
import warnings


class TorSession(requests.Session):
    # todo - add arguments for password
    # todo - test if CookieAuthentication is necessary
    def __init__(self, SOCKSPort=9050, ControlPort=9051, torrc_dir="etc/tor/torrc"):  # todo - test defaults in linux
        super().__init__()  # calls the init portion of the parent Session class

        with open("torrc_template", "r") as f:
            torrc_template = f.read()

        # todo - test to see if provided ports are already in use

        if not os.path.isfile(torrc_dir):
            with open(torrc_dir, "w") as f:
                f.write(torrc_template.format(
                    SOCKSPort=SOCKSPort,
                    ControlPort=ControlPort))

        # todo - add some kind of test to see if the Tor service is already running
        subprocess.call(['sudo', 'tor', '-f', torrc_dir])  # start the tor service

        self.proxies = {}
        self.proxies['http'] = 'socks5h://localhost:{}'.format(SOCKSPort)
        self.proxies['https'] = 'socks5h://localhost:{}'.format(ControlPort)

        self.ip = self.get("http://httpbin.org/ip").text
        self.SOCKSPort = SOCKSPort
        self.ControlPort = ControlPort

    def get_new_identity(self):
        max_retries = 5
        retries = 0
        while True:
            with Controller.from_port(port=self.ControlPort) as controller:
                controller.authenticate()  # todo - add authentication information
                controller.signal(Signal.NEWNYM)
            new_ip = self.get('http://httpbin.org/ip').text
            if new_ip != self.ip
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

