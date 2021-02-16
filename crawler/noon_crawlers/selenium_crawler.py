from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

# place your username and password here
# like this
# EMAIL = 'abcd@hotmail.com'
# PASSWORD = 'xyz'

BASE_URL_SAUDI = 'https://www.noon.com/saudi-en/'
BASE_URL_UAE = 'https://www.noon.com/uae-en/'

print('Starting chrome web driver .... ')

# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
driver = webdriver.Firefox()
driver.get(BASE_URL_UAE)
