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
    def __init__(self, SOCKSPort=9150, ControlPort=9151, torrc_dir=None):
        super().__init__()

        self.proxies = {}
        self.proxies['http'] = 'socks5h://localhost:{}'.format(SOCKSPort)
        self.proxies['https'] = 'socks5h://localhost:{}'.format(SOCKSPort)

        self.ip = self.get("http://httpbin.org/ip").text
        self.SOCKSPort = SOCKSPort
        self.ControlPort = ControlPort

    def pass_cookies(self, cookies):
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        }
        self.headers.update(headers)
        for cookie in cookies:
            c = {cookie['name']: cookie['value']}
            self.cookies.update(c)
