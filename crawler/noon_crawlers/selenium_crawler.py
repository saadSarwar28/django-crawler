from __future__ import print_function
# import geckodriver_autoinstaller
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import pyautogui
from crawler import settings
from apiclient import errors
import datetime
import json
import random
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
from selenium.webdriver import ActionChains, Proxy
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import os
import requests
import csv
from .models import *
from .google_drive_api_login import login_google
import pathlib

BASE_URL_SAUDI = 'https://www.noon.com/saudi-en/'
BASE_URL_UAE = 'https://www.noon.com/uae-en/'

categories = ['Electronics & Mobiles', 'Beauty & Health', 'Fashion', 'Home & Kitchen', 'Sports & Outdoors',
              'Toys & Games', 'Baby Products', 'Grocery', 'Automotive', 'Tools & Home Improvement', 'Books',
              'Pet Supplies', 'Stationery & Office Supplies', 'Music, Movies & TV Shows', 'Mahali']

# file ids of google drive
# for dev
# output_folder_ids = {
#     'UAE': '1ERv-klOUUdRFaBuunaUrd28IwA2uEpBK',
#     'KSA': '1O52z0vNdXNKx3g17DHM3_tQ1_5OHpi3P',
# }

# for deploy
output_folder_ids = {
    'UAE': '1i_bsSeQujS4-DHbCsC_BsqVFhfRbhaBm',
    'KSA': '1lo4t_0jYNxViTxve8I0TA_T1-EQpxWtY',
}


class Status:
    category = ''
    url = ''
    date = ''

    def __init__(self, category, url, date):
        self.category = category
        self.url = url
        self.date = date
        self.pages_scrapped = '0'
        self.error = 'None'
        self.error_image = 'None'
        self.error_in_skus = ''


def open_file():
    file = open('data.csv', 'at')
    if file.tell() == 0:
        file.write(
            'Category, NOON SKU, Product title, listing url, image url, Brand, REPORT date/time, no. of sellers, '
            'no. of FBN sellers, Buy Box seller, Buy Box Price, Total inventory,Sold quantity last day, '
            'sold qantity last 7 day, sold quantity last 30 day, listing with incorrect inventory, day 31 inventory, '
            'day 30 sold qty., day 30 inventory, day 29 sold qty., day 29 inventory, '
            'day 28 sold qty., day 28 inventory, '
            'day 27 sold qty., day 27 inventory, day 26 sold qty., day 26 inventory, '
            'day 25 sold qty., day 25 inventory, '
            'day 24 sold qty., day 24 inventory, day 23 sold qty., day 23 inventory, '
            'day 22 sold qty., day 22 inventory, '
            'day 21 sold qty., day 21 inventory, day 20 sold qty., day 20 inventory, '
            'day 19 sold qty., day 19 inventory, '
            'day 18 sold qty., day 18 inventory, day 17 sold qty., day 17 inventory, '
            'day 16 sold qty., day 16 inventory, '
            'day 15 sold qty., day 15 inventory, day 14 sold qty., day 14 inventory, '
            'day 13 sold qty., day 13 inventory, '
            'day 12 sold qty., day 12 inventory, day 11 sold qty.,	day 11 inventory, '
            'day 10 sold qty., day 10 inventory, '
            'day 9 sold qty., day 9 inventory, day 8 sold qty., day 8 inventory, day 7 sold qty., day 7 inventory, '
            'day 6 sold qty., day 6 inventory, day 5 sold qty., day 5 inventory, day 4 sold qty., day 4 inventory, '
            'day 3 sold qty., day 3 inventory, day 2 sold qty., day 2 inventory, day 1 sold qty., day 1 inventory'
        )
    return file


def get_input_file(file_key):
    service = login_google()
    page_token = None
    query = "name contains '" + file_key + "' and name contains 'Categories'"
    file_id = ''
    while True:
        response = service.files().list(q=query, spaces='drive',
                                        fields='nextPageToken, files(id, name, trashed, version)',
                                        pageToken=page_token).execute()
        version = 0
        for file in response.get('files', []):
            if file.get('trashed'):
                continue
            if int(file.get('version')) > version:
                version = int(file.get('version'))
                file_id = file.get('id')
            # print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    with open('input/' + file_key + '.xlsx', 'wb') as out:
        out.write(fh.read())
    input_file = pd.read_excel('input/' + file_key + '.xlsx', skiprows=[0])
    category_list = input_file['Category Name'].to_list()
    urls = input_file['URL'].to_list()
    return {'category_list': category_list, 'urls': urls}


def get_inventory_details(driver, sku):
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 200);")
    time.sleep(1)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='selectBoxFromComponent']"))
        ).click()
        total_inventory = len(driver.find_elements_by_xpath('//div[contains(@id, "react-select-")]'))
        id = 'react-select-selectBoxFromComponent-option-' + str(total_inventory - 1)
        last_scroll_ele = driver.find_element_by_id(id)
        driver.execute_script("return arguments[0].scrollIntoView(true);", last_scroll_ele)
        driver.execute_script("window.scrollTo(0, 200);")
        # last_scroll_ele.click()
    except Exception as error:
        # print(error)
        return 1
    time.sleep(1)
    driver.save_screenshot('screenshots/' + sku + '_' + datetime.datetime.now().strftime('%H-%M-%S') + '.png')
    time.sleep(1)
    # add_to_cart_button = driver.find_element_by_class_name('cart-button')
    # actions = ActionChains(driver)
    # actions.move_to_element(add_to_cart_button).perform()
    # add_to_cart_button.click()
    # time.sleep(2)
    # driver.find_element_by_tag_name('body').click()
    return total_inventory


def record_inventory_error(driver, error, sku):
    image_name = sku + '-' + str(random.random()).split('.')[1][0:8] + '.png'
    driver.save_screenshot('debug/inventory/' + image_name)
    file = open('debug/inventory-errors.txt', 'at')
    file.write('Error : ' + str(error) + '\n')
    file.write('SKU : ' + str(sku) + '\n')
    file.write('Error_image : ' + image_name + '\n')
    file.write('==================================' + '\n')
    file.close()


def clear_checkout(driver):
    url_list = driver.current_url.split('/')
    checkout_url = ''
    for x in range(0, 4):
        checkout_url = checkout_url + url_list[x] + '/'
    checkout_url = checkout_url + 'cart'
    driver.get(checkout_url)
    remove_buttons = driver.find_elements_by_xpath('//span[contains(text(), "Remove")]')
    for x in range(0, len(remove_buttons)):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Remove")]'))
        ).click()
        time.sleep(1)
    driver.back()


def get_total_inventory(driver, num_of_sellers, sku):
    num_of_fbn_sellers = 0
    try:
        total_inventory = get_inventory_details(driver, sku)
        estimator_right = driver.find_element_by_class_name('estimator_right')
        image_src = estimator_right.find_element_by_tag_name('img').get_attribute('src')
        if 'fulfilment_express_v2-en' in image_src:
            num_of_fbn_sellers = 1
        if num_of_sellers > 1:
            num_of_fbn_sellers = 0
            time.sleep(3)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "allOffers"))
            ).click()
            time.sleep(3)
            images = driver.find_elements_by_xpath('//div[@direction="row"]/div/img')
            for image in images:
                if 'fulfilment_express_v2-en' in image.get_attribute('src'):
                    num_of_fbn_sellers = num_of_fbn_sellers + 1
            driver.find_element_by_tag_name('body').click()
            # view_offers = driver.find_elements_by_class_name('selectedOffer')
            # for x in range(1, len(view_offers)):
            #     actions = ActionChains(driver)
            #     actions.move_to_element(view_offers[x]).perform()
            # view_offers[x].click()
            # time.sleep(3)
            # try:
            #     estimator_right = driver.find_element_by_class_name('estimator_right')
            #     image = estimator_right.find_element_by_xpath('//img[contains(@src, "fulfilment_express-en.png")]')
            #     num_of_fbn_sellers = num_of_fbn_sellers + 1
            # except:
            #     pass
            # grand_total_inventory = grand_total_inventory + get_inventory_details(driver)
            # time.sleep(1)
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "allOffers"))
            # ).click()
            # time.sleep(2)
            # clear_checkout(driver)
        # print('num of fbn sellers ===> ' + str(num_of_fbn_sellers))
        return {'num_fbn_sellers': num_of_fbn_sellers, 'total_inventory': str(total_inventory)}
    except Exception as error:
        record_inventory_error(driver, error, sku)
        return 'error fetching inventory'


def fetch_products_details(driver, product_sku, product_url, category_name, category_url):
    # opening new window
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(product_url)
    time.sleep(3)
    product_name = driver.find_element_by_xpath('//h1[contains(@data-qa, "name")]').text
    # all images, 200+ in total
    images = driver.find_elements_by_xpath('//img[contains(@src, "' + product_sku + '")]')
    image_url = ''
    # filtering image url
    for each in images:
        if product_sku in each.get_attribute('src') and not 'thumbnail' in each.get_attribute('src'):
            image_url = each.get_attribute('src')
            break
    brand = driver.find_element_by_xpath('//div[contains(@data-qa, "brand")]').text
    report_day_time = datetime.datetime.now().strftime('%D :: %I:%M %p')
    buy_box_seller = driver.find_elements_by_xpath('//a[@class="storeLink"]')[1].text
    buy_box_price = str(driver.find_element_by_xpath('//div[@class="priceNow"]').text).split(' ')[1]
    # num of sellers is checked by the number of offers text
    try:
        num_of_sellers = int(
            driver.find_element_by_xpath('//p[contains(text(), "offer") or contains(text(), "offers")]').text.split(
                ' ')[0]) + 1
    except Exception as error:
        num_of_sellers = 1
    data = get_total_inventory(driver, num_of_sellers, product_sku)
    total_inventory = data['total_inventory']
    num_of_fbn_sellers = data['num_fbn_sellers']
    driver.close()
    # Switch back to the first tab
    driver.switch_to.window(driver.window_handles[0])
    return {
        'category_name': category_name,
        'category_url': category_url,
        'product_sku': product_sku,
        'product_name': product_name,
        'product_url': product_url,
        'image_url': image_url,
        'brand': brand,
        'report_day_time': report_day_time,
        'num_of_sellers': num_of_sellers,
        'num_of_fbn_sellers': num_of_fbn_sellers,
        'buy_box_seller': buy_box_seller,
        'buy_box_price': buy_box_price,
        'total_inventory': total_inventory
    }


def initialize_firefox():
    # geckodriver_autoinstaller.install()
    # port = refresh_proxy_port()
    # PROXY = 'localhost:' + port
    # proxy = Proxy()
    # proxy.http_proxy = PROXY
    # proxy.ftp_proxy = PROXY
    # proxy.sslProxy = PROXY
    # proxy.no_proxy = "localhost"  # etc... ;)
    # proxy.proxy_type = ProxyType.MANUAL
    # limunati customer info
    # proxy.socksUsername = 'lum-customer-hl_768420d0-zone-static-country-ae'
    # proxy.socksPassword = 'auudw0lxh4pp'
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    # proxy.add_to_capabilities(capabilities)
    driver_path = 'geckodriver.exe'
    # driver = webdriver.Chrome(desired_capabilities=capabilities)
    firefox_options = webdriver.FirefoxOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox') # required when running as root user.
    # otherwise you would get no sandbox errors.
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    driver = webdriver.Firefox(
        executable_path=driver_path,
        # desired_capabilities=capabilities,
        options=firefox_options,
        firefox_profile=firefox_profile
    )
    return driver


def refresh_proxy_port():
    # delete all previous ports
    # response = requests.get('http://localhost:22999/api/proxies_running')
    # response = json.loads(response.content)
    # for each in response:
    #     requests.delete("http://127.0.0.1:22999/api/proxies/" + str(each['port']))
    # proxies = ProxyPorts.objects.all().order_by('-port_number')
    # if len(proxies) < 1:
    #     new_port = 24000
    #     ProxyPorts(port_number=new_port).save()
    # else:
    #     new_port = proxies[0].port_number + 1
    #     ProxyPorts(port_number=new_port).save()
    header = {"Content-Type": "application/json"}
    # to get a new port
    # data = {"proxy": {"port": 24000, "zone": "static", "proxy_type": "persist", "customer": "h1_768420d0",
    #                   "password": "auudw01xh4pp", "whitelist_ips": []}}
    # requests.post(url="http://127.0.0.1:22999/api/proxies", data=json.dumps(data), headers=header)
    requests.get(url="http://127.0.0.1:22999/api/refresh_sessions/24000", headers=header)
    return '24000'


def initialize_chrome():
    # port = refresh_proxy_port()
    # PROXY = 'localhost:' + port
    # proxy = Proxy()
    # proxy.http_proxy = PROXY
    # proxy.ftp_proxy = PROXY
    # proxy.sslProxy = PROXY
    # proxy.no_proxy = "localhost"  # etc... ;)
    # proxy.proxy_type = ProxyType.MANUAL
    # capabilities = webdriver.DesiredCapabilities.CHROME
    # proxy.add_to_capabilities(capabilities)
    driver_path = 'chromedriver.exe'
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_extension('browsec.crx')
    # prefs = {'profile.managed_default_content_settings.images': 2}
    # chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.add_argument('--no-proxy-server')
    # chrome_options.add_argument("--proxy-server='direct://'");
    # chrome_options.add_argument("--proxy-bypass-list=*");
    # chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument('--no-sandbox') # required when running as root user.
    # otherwise you would get no sandbox errors.
    driver = webdriver.Chrome(
        executable_path=driver_path,
        # desired_capabilities=capabilities,
        options=chrome_options
    )
    # driver = enable_browsec(driver)
    return driver


def enable_browsec(driver):
    time.sleep(10)
    pyautogui.click(pyautogui.locateCenterOnScreen('browsec_icon.png', confidence=0.9))
    time.sleep(5)
    pyautogui.click(pyautogui.locateCenterOnScreen('browsec_turn_on.png', confidence=0.9))
    time.sleep(10)
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return driver


def check_category_already_scraped(category_name, country, fetch_day):
    if Category.objects.filter(
            name=category_name,
            country=country,
            month=datetime.datetime.now().date().strftime('%B'),
            created_at=datetime.date.today(),
    ).exists():
        return True
    return False


def start_crawling(country, number_of_pages=4):
    fetch_day = get_fetch_day_count()
    # proxy_port_id = save_bandwidth_status(country=country, start=True)
    input_file = get_input_file(country)
    category_list, urls = input_file['category_list'], input_file['urls']
    status_report = []
    today = datetime.datetime.now().strftime('%D')
    for category_url, category_name in zip(urls, category_list):
        if check_category_already_scraped(category_name, country, fetch_day):
            continue
        data = []
        status = {
            'category': category_name,
            'url': category_url,
            'date': today,
            'pages_scrapped': '',
            'error_in_skus': '',
            'error': '',
            'error_image': ''
        }
        # scrap first two pages
        number_of_sku = 0
        for x in range(1, number_of_pages + 1):
            status['pages_scrapped'] = str(x)
            try:
                driver = initialize_chrome()
                if '?' in category_url:
                    driver.get(category_url + '&page=' + str(x) + '&limit=60')
                else:
                    driver.get(category_url + '?page=' + str(x) + '&limit=60')
            except Exception as error:
                print('Error getting url => ' + str(error))
                driver = initialize_chrome()
                if '?' in category_url:
                    driver.get(category_url + '&page=' + str(x) + '&limit=60')
                else:
                    driver.get(category_url + '?page=' + str(x) + '&limit=60')
            time.sleep(2)
            # fetching divs of all products
            try:
                product_divs = driver.find_elements_by_class_name('productContainer')
                product_skus, product_urls, sku_errors = [], [], []
                for div in product_divs:
                    product_skus.append(div.find_element_by_tag_name('a').get_attribute('id').split('-')[1])
                    product_urls.append(div.find_element_by_tag_name('a').get_attribute('href'))
                for product_sku, product_url in zip(product_skus, product_urls):
                    try:
                        product_details = fetch_products_details(driver, product_sku, product_url, category_name,
                                                                 category_url)
                        data.append(product_details)
                        number_of_sku = number_of_sku + 1
                        # print(number_of_sku)
                        # print(product_details)
                    except Exception as error:
                        try:
                            status['error_in_skus'] = product_sku + ' - ' + status['error_in_skus']
                            image_name = product_sku + '-' + str(random.random()).split('.')[1][0:8] + '.png'
                            driver.save_screenshot('debug/sku/' + image_name)
                            sku_errors.append({'sku': product_sku, 'error': error, 'error_image': image_name})
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except Exception as error_:
                            pass
                log_sku_errors(sku_errors)
            except Exception as error:
                try:
                    image_name = category_name + '-' + str(random.random()).split('.')[1][0:8] + '.png'
                    driver.save_screenshot('debug/' + image_name)
                    status['error'] = error
                    status['error_image'] = image_name
                    driver.close()
                except:
                    pass
        try:
            driver.close()
        except:
            pass
        for each_product in data:
            save_product_in_database(each_product, fetch_day, country)
        save_remaining_products_days_by_category(category_name, country, fetch_day)
        calculate_sold_quantities(category_name, country)
        file_name = write_data_to_file(category_name, country)
        # upload_files_to_google_drive(file_name, country)
        status_report.append(status)
        Category(name=category_name, country=country, fetch_day_count=fetch_day, num_of_skus=number_of_sku,
                 fully_scraped=True, num_of_pages_scraped=number_of_pages).save()
    write_status_report(country, status_report)
    # save_bandwidth_status(id=proxy_port_id)
    # send_email(country, number_of_pages, number_of_sku)
    # delete_previous_files_from_google_drive()


def save_remaining_products_days_by_category(category, country, fetch_day):
    products = Product.objects.filter(category=category, country=country)
    for product in products:
        latest_day = Day.objects.filter(product=product).latest('day')
        if latest_day.day < datetime.date.today():
            Day(
                product=product,
                day_count=fetch_day,
                sold_quantity=-1,
                inventory=-1,
                day=datetime.date.today(),
            ).save()


def save_remaining_products_days():
    fetch_day = get_fetch_day_count()
    products = Product.objects.all()
    for product in products:
        days = Day.objects.filter(product=product, day=datetime.date.today())
        if len(days) < 1:
            Day(day_count=fetch_day, sold_quantity=-1, inventory=-1, product=product, day=datetime.date.today()).save()


def save_bandwidth_status(country='', start=False, id=None):
    if start:
        response = requests.get('http://127.0.0.1:22999/api/recent_stats')
        response = json.loads(response.content)
        bandwidth_out = response['ports']['24000']['out_bw']
        bandwidth_out = bytesto(bandwidth_out, to='m')
        bandwidth_in = response['ports']['24000']['in_bw']
        bandwidth_in = bytesto(bandwidth_in, to='m')
        total_bandwidth = bandwidth_out + bandwidth_in
        proxy_port = ProxyPorts(port_number=24000, site=country, starting_bandwidth=float(total_bandwidth))
        proxy_port.save()
        return proxy_port.id
    else:
        proxy_port = ProxyPorts.objects.get(id=id)
        response = requests.get('http://127.0.0.1:22999/api/recent_stats')
        response = json.loads(response.content)
        bandwidth_out = response['ports']['24000']['out_bw']
        bandwidth_out = bytesto(bandwidth_out, to='m')
        bandwidth_in = response['ports']['24000']['in_bw']
        bandwidth_in = bytesto(bandwidth_in, to='m')
        total_bandwidth = bandwidth_out + bandwidth_in
        proxy_port.ending_bandwidth = total_bandwidth
        proxy_port.bandwidth_utilized = float(total_bandwidth - float(proxy_port.starting_bandwidth))
        proxy_port.save()
    return


def save_product_in_database(data, fetch_day, country):
    if Product.objects.filter(sku=str(data['product_sku']).strip(), country=country).exists():
        try:
            product = Product.objects.get(sku=str(data['product_sku']).strip(), country=country)
        except Exception:
            product = Product.objects.filter(sku=str(data['product_sku']).strip(), country=country)
            product = product[0]
        product.category = data['category_name']
        product.product_title = data['product_name']
        product.listing_url = data['product_url']
        product.image_url = data['image_url']
        product.brand = data['brand']
        product.report_date_time = data['report_day_time']
        product.no_of_sellers = int(data['num_of_sellers'])
        product.no_of_fbn_sellers = int(data['num_of_fbn_sellers'])
        product.buy_box_seller = data['buy_box_seller']
        product.buy_box_Price = float(data['buy_box_price'])
        product.total_inventory = data['total_inventory']
        product.updated_today = True
        product.save()
        latest_day = Day.objects.filter(product=product).latest('day')
        if latest_day.day == datetime.date.today():
            latest_day.inventory = int(data['total_inventory'])
            latest_day.save()
        else:
            Day(
                product=product,
                day_count=latest_day.day_count + 1,
                inventory=int(data['total_inventory']),
                day=datetime.date.today(),
            ).save()
    else:
        new_product = Product(
            country=country,
            category=data['category_name'],
            sku=str(data['product_sku']).strip(),
            product_title=data['product_name'],
            listing_url=data['product_url'],
            image_url=data['image_url'],
            brand=data['brand'],
            report_date_time=data['report_day_time'],
            no_of_sellers=int(data['num_of_sellers']),
            no_of_fbn_sellers=int(data['num_of_fbn_sellers']),
            buy_box_seller=data['buy_box_seller'],
            buy_box_Price=float(data['buy_box_price']),
            total_inventory=data['total_inventory'],
            updated_today=True
        )
        new_product.save()
        today = datetime.date.today()
        for x in range(31):
            if x == (0):
                Day(day_count=fetch_day, inventory=int(data['total_inventory']), product=new_product, day=today).save()
            else:
                Day(day_count=x + 1, sold_quantity=-1, inventory=-1, product=new_product, day=today).save()
            today = today - datetime.timedelta(days=1)


def calculate_sold_quantities(category_name, country):
    products = Product.objects.filter(category=category_name, country=country)
    for product in products:
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:2]
        if len(previous_days) > 1:
            latest_day = previous_days[0]
            previous_day = previous_days[1]
            if not previous_day.inventory == -1 and not latest_day.inventory == -1:
                if previous_day.inventory <= latest_day.inventory:
                    previous_day.sold_quantity = 0
                    previous_day.save()
                else:
                    previous_day.sold_quantity = previous_day.inventory - latest_day.inventory
                    previous_day.save()
            else:
                previous_day.sold_quantity = -1
                previous_day.save()

        total_sold_week = 0
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:8]
        consecutive_days = True
        for index, day in enumerate(previous_days):
            if index == 0:
                continue
            if day.sold_quantity == -1:
                consecutive_days = False
                break
            else:
                total_sold_week = total_sold_week + day.sold_quantity
        if consecutive_days and len(previous_days) > 7:
            product.sold_quantity_last_7_day = total_sold_week
        else:
            product.sold_quantity_last_7_day = -1

        total_sold_a_month = 0
        consecutive_days = True
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:31]
        for index, day in enumerate(previous_days):
            if index == 0:
                continue
            if day.sold_quantity == -1:
                consecutive_days = False
                break
            else:
                total_sold_a_month = total_sold_a_month + day.sold_quantity
        if consecutive_days and len(previous_days) > 30:
            product.sold_quantity_last_30_day = total_sold_a_month
        else:
            product.sold_quantity_last_30_day = -1
        product.save()


def calculate_all_sold_quantities(category_name, country):
    products = Product.objects.filter(category=category_name, country=country)
    for product in products:
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('day')
        previous_day = None
        for index, day in enumerate(previous_days):
            if index == 0:
                previous_day = day
                continue
            if (day.inventory == -1) or (previous_day.inventory == -1):
                previous_day.sold_quantity = -1
                previous_day.save()
                previous_day = day
                continue
            if day.inventory >= previous_day.inventory:
                previous_day.sold_quantity = 0
                previous_day.save()
                previous_day = day
                continue
            previous_day.sold_quantity = previous_day.inventory - day.inventory
            previous_day.save()
            previous_day = day

        total_sold_week = 0
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:8]
        consecutive_days = True
        for index, day in enumerate(previous_days):
            if index == 0:
                continue
            if day.sold_quantity == -1:
                consecutive_days = False
                break
            else:
                total_sold_week = total_sold_week + day.sold_quantity
        if consecutive_days and len(previous_days) > 7:
            product.sold_quantity_last_7_day = total_sold_week
        else:
            product.sold_quantity_last_7_day = -1

        total_sold_a_month = 0
        consecutive_days = True
        previous_days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:31]
        for index, day in enumerate(previous_days):
            if index == 0:
                continue
            if day.sold_quantity == -1:
                consecutive_days = False
                break
            else:
                total_sold_a_month = total_sold_a_month + day.sold_quantity
        if consecutive_days and len(previous_days) > 30:
            product.sold_quantity_last_30_day = total_sold_a_month
        else:
            product.sold_quantity_last_30_day = -1
        product.save()


def write_status_report(country, status_report):
    with open('Status-reports/' + str(country) + ' - ' + datetime.datetime.now().strftime('%d') + '.csv', 'w',
              newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['category', 'url', 'date', 'pages_scrapped', 'error', 'error_image', 'error_in_skus'])
        for row in status_report:
            writer.writerow(
                [
                    row['category'],
                    row['url'],
                    row['date'],
                    row['pages_scrapped'],
                    row['error'],
                    row['error_image'],
                    row['error_in_skus'],
                ]
            )


def create_fetch_day():
    days = FetchDay.objects.filter(month=datetime.datetime.now().date().strftime('%B'))
    if len(days) < 1:
        FetchDay(
            month=datetime.datetime.now().date().strftime('%B'),
            day=1,
            created_at=datetime.date.today()
        ).save()
        return 1
    else:
        fetch_day = len(days) + 1
        FetchDay(
            month=datetime.datetime.now().date().strftime('%B'),
            day=fetch_day,
            created_at=datetime.date.today()
        ).save()
        return fetch_day


def get_fetch_day_count():
    return FetchDay.objects.filter(month=datetime.datetime.now().date().strftime('%B')).count()


def write_data_to_file(category_name, country):
    products = Product.objects.filter(category=category_name, country=country)
    fetch_days = FetchDay.objects.all().order_by('-created_at')[:31]
    total_fetched_days = len(fetch_days)
    data = []
    data.append(
        [
            'Category',
            'NOON SKU',
            'Product title',
            'listing url',
            'image url',
            'Brand',
            'REPORT date/time',
            'no. of sellers',
            'no. of FBN sellers',
            'Buy Box seller',
            'Buy Box Price',
            'Latest Buy Box inventory',
            # 'Sold quantity last day',
            'sold quantity last 7 days',
            'sold quantity last 30 days',
        ]
    )

    for index in range(0, total_fetched_days):
        if index == 0:
            data[0].append('day ' + fetch_days[index].created_at.strftime('%m/%d') + ' Inventory')
        else:
            data[0].append('day ' + fetch_days[index].created_at.strftime('%m/%d') + ' sold quantity')
            data[0].append('day ' + fetch_days[index].created_at.strftime('%m/%d') + ' inventory')

    for product in products:
        days = Day.objects.filter(product=product).distinct('day').order_by('-day')[:31]
        inventory = []
        for index in range(0, len(days)):
            if index != 0:
                inventory.append(days[index].sold_quantity)
            inventory.append(days[index].inventory)
        if product.sold_quantity_last_7_day == -1:
            sold_quantity_last_7_day = 'Not applicable yet'
        else:
            sold_quantity_last_7_day = product.sold_quantity_last_7_day
        if product.sold_quantity_last_30_day == -1:
            sold_quantity_last_30_day = 'Not applicable yet'
        else:
            sold_quantity_last_30_day = product.sold_quantity_last_30_day
        data.append(
            [
                product.category,
                product.sku,
                product.product_title,
                product.listing_url,
                product.image_url,
                product.brand,
                product.report_date_time,
                product.no_of_sellers,
                product.no_of_fbn_sellers,
                product.buy_box_seller,
                product.buy_box_Price,
                product.total_inventory,
                sold_quantity_last_7_day,
                sold_quantity_last_30_day,
            ] + inventory)

    data.insert(0, [category_name + '-' + country, ])
    file_name = 'data/' + country + '/' + category_name + '-' + fetch_days[0].created_at.strftime('%d') + '.xlsx'
    df = pd.DataFrame.from_records(data)
    df.to_excel(file_name)
    for product in products:
        product.updated_today = False
        product.save()
    return file_name
    # with open(file_name, 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     head = category_name + '-' + country
    #     writer.writerow([head, ])
    #     writer.writerow(data['headers'])
    #     for row in data['data']:
    #         writer.writerow(row)


def log_sku_errors(sku_errors):
    file = open('debug/sku/sku_errors.csv', 'at', encoding='utf-8')
    if file.tell() == 0:
        file.write('SKU,error,image name\n')
    for each_sku in sku_errors:
        file.write(each_sku['sku'] + ',' + each_sku['error'] + ',' + each_sku['error_image'] + '\n')
    file.close()


def bytesto(bytes, to, bsize=1024):
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    # r = float(bytes)
    return bytes / (bsize ** a[to])


def send_email(country):
    to = 'noondata2021@gmail.com'
    subject = 'Noon Scraping Status Report for ' + str(country)
    fetch_day = get_fetch_day_count()
    categories = Category.objects.filter(country=country, fetch_day_count=fetch_day)
    number_of_sku = 0
    for each in categories:
        number_of_sku = each.num_of_skus + number_of_sku
    # proxy_port = ProxyPorts.objects.filter(site=country).latest('id')
    message = 'Scraping for ' + datetime.datetime.now().strftime('%D') + ' has finished. Please check you google ' \
                                                                         'drive for updated files.\n'
    message = message + 'Scrapping details. \n'
    message = message + 'Number of categories fetched : ' + str(len(categories)) + '\n'
    message = message + 'Number of pages scraped per category : ' + str(2) + '\n'
    message = message + 'Targeted Number of SKUs per category : ' + str(2 * 50) + '\n'
    message = message + 'Total Number of SKUs fetched for site ' + country + ' : ' + str(number_of_sku) + '\n'
    # message = message + 'Bandwidth utilized : ' + str(proxy_port.bandwidth_utilized) + '\n'
    # message = message + 'Time taken : ' + str(proxy_port.updated_at - proxy_port.created_at).split('.')[0] + \
    #           '(hour/minute/second)\n\n'
    message = message + '<=======================>'

    debug_file = open('email-debug.txt', 'at')
    debug_file.write('From = ' + str(settings.EMAIL_HOST_USER) + '\n')
    debug_file.write('To = ' + str(to) + '\n')

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    files = os.listdir('data/' + country)
    for file in files or []:
        with open('data/' + country + '/' + file, "rb") as selected_file:
            part = MIMEApplication(
                selected_file.read(),
                Name=basename(file)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
        msg.attach(part)
    try:
        email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        debug_file.write('Server connected successfully.\n')
        email_server.ehlo()
        email_server.starttls()
        email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        email_server.ehlo()
        debug_file.write('Logged in successfully.\n')
        # smtp = smtplib.SMTP(email_server)
        email_server.sendmail(settings.EMAIL_HOST_USER, [to, ], msg.as_string())
        email_server.close()
        debug_file.write('Email sent successfully.\n')
        # recipient_list = [to, ]
        # message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        #         """ % (settings.EMAIL_HOST_USER, ", ".join(recipient_list), subject, message)
        # email_server.sendmail(settings.EMAIL_HOST_USER, recipient_list, message)
        # email_server.close()
    except Exception as error:
        # print(error)
        debug_file.write('Error thrown.\n')
        debug_file.write('Error details => ' + str(error) + '\n')
    debug_file.write(' ======================== \n')
    debug_file.close()


def delete_extra_days():
    products = Product.objects.all()
    for product in products:
        today = datetime.date.today()
        for x in range(0, 30):
            days = Day.objects.filter(product=product, day=today)
            if len(days) > 1:
                for day in days:
                    if day.sold_quantity == -1 and day.inventory == -1:
                        day.delete()


def add_extra_days():
    fetch_day = get_fetch_day_count()
    products = Product.objects.all()
    for product in products:
        today = datetime.date.today()
        for x in range(0, 30):
            days = Day.objects.filter(product=product, day=today)
            if len(days) < 1:
                Day(product=product, sold_quantity=-1, inventory=-1, day_count=fetch_day, day=today).save()
            today = today - datetime.timedelta(days=1)
