from selenium import webdriver
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy



driver_path = 'chromedriver.exe'

chrome_options = webdriver.ChromeOptions()

req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
proxies = req_proxy.get_proxy_list() #this will create proxy list

# int(str(random.random())[2:4])
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.