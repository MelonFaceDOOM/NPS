from selenium import webdriver
import subprocess

driver = webdriver.Firefox()


subprocess.call(['sudo', './venv/bin/python', 'test2.py'])