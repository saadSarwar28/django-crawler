from __future__ import print_function

import smtplib
from crawler import settings
from apiclient import errors
import datetime
import json
import random
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains, Proxy
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
# import os
import requests
import csv
from .models import *
from .google_drive_api_login import login_google

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
                                        fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
        for file in response.get('files', []):
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
    with open(file_key + '.xlsx', 'wb') as out:
        out.write(fh.read())
    input_file = pd.read_excel(file_key + '.xlsx', skiprows=[0])
    category_list = input_file['Category Name'].to_list()
    urls = input_file['URL'].to_list()
    return {'category_list': category_list, 'urls': urls}


def get_inventory_details(driver):
    time.sleep(1)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='selectBoxFromComponent']"))
        ).click()
    except Exception as error:
        print(error)
        return 1
    time.sleep(1)
    total_inventory = len(driver.find_elements_by_xpath('//div[contains(@id, "react-select-")]'))
    id = 'react-select-selectBoxFromComponent-option-' + str(total_inventory - 1)
    last_scroll_ele = driver.find_element_by_id(id)
    driver.execute_script("return arguments[0].scrollIntoView(true);", last_scroll_ele)
    last_scroll_ele.click()
    time.sleep(1)
    add_to_cart_button = driver.find_element_by_class_name('cart-button')
    actions = ActionChains(driver)
    actions.move_to_element(add_to_cart_button).perform()
    add_to_cart_button.click()
    time.sleep(2)
    driver.find_element_by_tag_name('body').click()
    return total_inventory


def record_inventory_error(driver, error, sku):
    image_name = sku + '-' + str(random.random()).split('.')[1][0:8] + '.png'
    driver.save_screenshot('../debug/inventory/' + image_name)
    file = open('inventory-errors.txt', 'at')
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
        total_inventory = get_inventory_details(driver)
        # try:
        try:
            estimator_right = driver.find_element_by_class_name('estimator_right')
            image = estimator_right.find_element_by_xpath('//img[@src="https://k.nooncdn.com/s/app/com/noon/images/fulfilment_express-en.png"]')
            num_of_fbn_sellers = 1
        except:
            pass
        if num_of_sellers > 1:
            num_of_fbn_sellers = 0
            time.sleep(3)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "allOffers"))
            ).click()
            time.sleep(3)
            images = driver.find_elements_by_xpath('//div[@direction="row"]/div/img')
            for image in images:
                if image.get_attribute(
                        'src') == 'https://k.nooncdn.com/s/app/com/noon/images/fulfilment_express-en.png':
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
    buy_box_seller = driver.find_element_by_xpath('//a[@class="storeLink"]').text
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
    port = refresh_proxy_port()
    PROXY = 'localhost:' + port
    proxy = Proxy()
    proxy.http_proxy = PROXY
    proxy.ftp_proxy = PROXY
    proxy.sslProxy = PROXY
    # proxy.no_proxy = "localhost"  # etc... ;)
    proxy.proxy_type = ProxyType.MANUAL
    # limunati customer info
    # proxy.socksUsername = 'lum-customer-hl_768420d0-zone-static-country-ae'
    # proxy.socksPassword = 'auudw0lxh4pp'
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    proxy.add_to_capabilities(capabilities)
    driver_path = 'geckodriver.exe'
    # driver = webdriver.Chrome(desired_capabilities=capabilities)
    firefox_options = webdriver.FirefoxOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox') # required when running as root user.
    # otherwise you would get no sandbox errors.
    driver = webdriver.Firefox(
        executable_path=driver_path,
        desired_capabilities=capabilities,
        options=firefox_options
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
    port = refresh_proxy_port()
    PROXY = 'localhost:' + port
    proxy = Proxy()
    proxy.http_proxy = PROXY
    proxy.ftp_proxy = PROXY
    proxy.sslProxy = PROXY
    proxy.no_proxy = "localhost"  # etc... ;)
    proxy.proxy_type = ProxyType.MANUAL
    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)
    driver_path = 'chromedriver.exe'
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--proxy-server='direct://'");
    chrome_options.add_argument("--proxy-bypass-list=*");
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox') # required when running as root user.
    # otherwise you would get no sandbox errors.
    driver = webdriver.Chrome(
        executable_path=driver_path,
        desired_capabilities=capabilities,
        options=chrome_options
    )
    return driver


def start_crawling(country, number_of_pages=4):
    fetch_day = get_fetch_day_count()
    proxy_port_id = save_bandwidth_status(start=True)
    input_file = get_input_file(country)
    category_list, urls = input_file['category_list'], input_file['urls']
    categories_fetched = len(category_list)
    status_report = []
    today = datetime.datetime.now().strftime('%D')
    for category_url, category_name in zip(urls, category_list):
        # initializing chrome here means new ip for every 500 SKUs
        data = []
        driver = initialize_chrome()
        status = Status(category_name, category_url, today)
        # scrap first ten pages
        for x in range(1, number_of_pages):
            status.pages_scrapped = str(x)
            driver.get(category_url + '?page=' + str(x))
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
                        data.append(
                            fetch_products_details(driver, product_sku, product_url, category_name, category_url)
                        )
                    except Exception as error:
                        status.error_in_skus = product_sku + ' - ' + status.error_in_skus
                        image_name = product_sku + '-' + str(random.random()).split('.')[1][0:8] + '.png'
                        driver.save_screenshot('../debug/sku/' + image_name)
                        sku_errors.append({'sku': product_sku, 'error': error, 'error_image': image_name})
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                log_sku_errors(sku_errors)
            except Exception as error:
                image_name = category_name + '-' + str(random.random()).split('.')[1][0:8] + '.png'
                driver.save_screenshot('../debug/' + image_name)
                status.error = error
                status.error_image = image_name
        driver.close()
        # backup file for each category and day
        with open(category_name + '-' + datetime.datetime.today().strftime('%d'), 'w', newline='') as file:
            writer = csv.writer(file)
            for each_product in data:
                writer.writerow(each_product)
        for each_product in data:
            save_product_in_database(each_product, fetch_day)
        save_remaining_products_days_by_category(category_name, fetch_day)
        file_name = write_data_to_file(category_name, country)
        upload_files_to_google_drive(file_name, country)
        status_report.append(status.__dict__)
    save_remaining_products_days(fetch_day)
    write_status_report(status_report)
    save_bandwidth_status(id=proxy_port_id)
    send_email(country, categories_fetched, number_of_pages)
    delete_previous_files_from_google_drive()


def save_remaining_products_days_by_category(category, fetch_day):
    products = Product.objects.filter(category=category)
    for product in products:
        days = Day.objects.filter(product=product)
        if len(days) < fetch_day:
            Day(day_count=fetch_day, product=product).save()


def save_remaining_products_days(fetch_day):
    products = Product.objects.all()
    for product in products:
        days = Day.objects.filter(product=product)
        if len(days) < fetch_day:
            Day(day_count=fetch_day, product=product).save()


def save_bandwidth_status(start=False, id=None):
    if start:
        response = requests.get('http://127.0.0.1:22999/api/recent_stats')
        response = json.loads(response.content)
        bandwidth_out = response['ports']['24000']['out_bw']
        bandwidth_out = bytesto(bandwidth_out, to='m')
        bandwidth_in = response['ports']['24000']['in_bw']
        bandwidth_in = bytesto(bandwidth_in, to='m')
        total_bandwidth = bandwidth_out + bandwidth_in
        proxy_port = ProxyPorts(port_number=24000, starting_bandwidth=float(total_bandwidth))
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


def save_product_in_database(data, fetch_day):
    if Product.objects.filter(sku=data['product_sku']).exists():
        product = Product.objects.get(sku=data['product_sku'])
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
        previous_days = Day.objects.filter(product=product).order_by('-day_count')
        if data['total_inventory'] != 'error fetching inventory' and len(
                Day.objects.filter(product=product)) > 0:
            if previous_days[0].inventory != 'error fetching inventory':
                if int(data['total_inventory']) >= int(previous_days[0].inventory):
                    sold_quantity = 0
                else:
                    sold_quantity = int(previous_days[0].inventory) - int(data['total_inventory'])
            else:
                sold_quantity = 0
        else:
            sold_quantity = 0
        product.sold_quantity_last_day = sold_quantity
        index = 0
        total_sold = 0
        if len(previous_days) > 5:
            for day in previous_days:
                total_sold = total_sold + day.sold_quantity
                if index == 6:
                    product.sold_quantity_last_7_day = total_sold
                if index == 29:
                    product.sold_quantity_last_30_day = total_sold
                index = index + 1
        product.save()
        Day(day_count=len(previous_days) + 1, sold_quantity=sold_quantity,
            inventory=int(data['total_inventory']), product=product).save()
    else:
        new_product = Product(
            category=data['category_name'],
            sku=data['product_sku'],
            product_title=data['product_name'],
            listing_url=data['product_url'],
            image_url=data['image_url'],
            brand=data['brand'],
            report_date_time=data['report_day_time'],
            no_of_sellers=int(data['num_of_sellers']),
            no_of_fbn_sellers=int(data['num_of_fbn_sellers']),
            buy_box_seller=data['buy_box_seller'],
            buy_box_Price=float(data['buy_box_price']),
            total_inventory=data['total_inventory']
        )
        new_product.save()
        for x in range(0, fetch_day):
            if x == (fetch_day - 1):
                Day(day_count=fetch_day, inventory=int(data['total_inventory']),
                    product=new_product).save()
            else:
                Day(day_count=x + 1, product=new_product).save()


def write_status_report(status_report):
    with open('status-report-' + datetime.datetime.now().strftime('%d') + '.csv', 'w', newline='') as file:
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
        FetchDay(month=datetime.datetime.now().date().strftime('%B'), day=1).save()
        return 1
    else:
        fetch_day = len(days) + 1
        FetchDay(month=datetime.datetime.now().date().strftime('%B'), day=fetch_day).save()
        return fetch_day


def get_fetch_day_count():
    return len(FetchDay.objects.all())


def write_data_to_file(category_name, country):
    products = Product.objects.filter(category=category_name)
    fetch_days = FetchDay.objects.filter(month=datetime.datetime.now().date().strftime('%B')).order_by('-created_at')
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
            data[0].append('day ' + fetch_days[index].created_at.date().strftime('%m/%d') + ' Inventory')
        else:
            data[0].append('day ' + fetch_days[index].created_at.date().strftime('%m/%d') + ' sold quantity')
            data[0].append(
                'day ' + fetch_days[index].created_at.date().strftime('%m/%d') + ' inventory')

    for product in products:
        days = Day.objects.filter(
            product=product,
            month=datetime.datetime.now().date().strftime('%B')
        ).order_by('-day_count')
        inventory = []
        for index in range(0, len(days)):
            if index != 0:
                inventory.append(days[index].sold_quantity)
            inventory.append(days[index].inventory)
        # if str(product.sold_quantity_last_day) == 'None':
        #     sold_quantity_last_day = 'Not applicable yet'
        # else:
        #     sold_quantity_last_day = product.sold_quantity_last_day
        if str(product.sold_quantity_last_7_day) == 'None':
            sold_quantity_last_7_day = 'Not applicable yet'
        else:
            sold_quantity_last_7_day = product.sold_quantity_last_7_day
        if str(product.sold_quantity_last_30_day) == 'None':
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
                # product.sold_quantity_last_day,
                sold_quantity_last_7_day,
                sold_quantity_last_30_day,
            ] + inventory)


    data.insert(0, [category_name + '-' + country, ])
    file_name = category_name + '-' + fetch_days[0].created_at.strftime('%d') + '.xlsx'
    df = pd.DataFrame.from_records(data)
    df.to_excel(file_name)
    return file_name
    # with open(file_name, 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     head = category_name + '-' + country
    #     writer.writerow([head, ])
    #     writer.writerow(data['headers'])
    #     for row in data['data']:
    #         writer.writerow(row)


def upload_files_to_google_drive(file_name, country):
    folder_id = output_folder_ids[country]
    drive_service = login_google()
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_name, mimetype='application/vnd.openxmlformats-', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    FilesToDelete(file_id=file['id']).save()


def delete_previous_files_from_google_drive():
    drive_service = login_google()
    files = FilesToDelete.objects.filter(created_at__lt=datetime.datetime.now().date())
    for file in files:
        drive_service.files().delete(fileId=file.file_id).execute()
        file.delete()


def log_sku_errors(sku_errors):
    file = open('../debug/sku_errors.csv', 'at')
    if file.tell() == 0:
        file.write('SKU,error,image name\n')
    for each_sku in sku_errors:
        file.write(each_sku['sku'] + ',' + each_sku['error'] + ',' + each_sku['error_image'] + '\n')
    file.close()


def bytesto(bytes, to, bsize=1024):
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    # r = float(bytes)
    return bytes / (bsize ** a[to])


def send_email(country, categories_fetched, number_of_pages):
    to = 'noondata2021@gmail.com'
    subject = 'Noon Scraping Status Report for ' + str(country)
    proxy_port = ProxyPorts.objects.latest('id')
    message = 'Scraping for ' + datetime.datetime.now().strftime('%D') + ' has finished. Please check you google ' \
                                                                         'drive for updated files.\n'
    message = message + 'Scrapping details. \n'
    message = message + 'Number of categories fetched : ' + str(categories_fetched) + '\n'
    message = message + 'Number of pages scraped per category : ' + str(number_of_pages) + '\n'
    message = message + 'Number of SKUs per category : ' + str(number_of_pages * 50) + '\n'
    message = message + 'Bandwidth utilized : ' + str(proxy_port.bandwidth_utilized) + '\n'
    message = message + 'Time taken : ' + str(proxy_port.updated_at - proxy_port.created_at).split('.')[0] + \
              '(hour/minute/second)\n\n'
    message = message + '<=======================>'
    file = open('email-debug.txt', 'at')
    file.write('From = ' + str(settings.EMAIL_HOST_USER) + '\n')
    file.write('To = ' + str(to) + '\n')
    try:
        email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        file.write('Server connected successfully.\n')
        email_server.ehlo()
        email_server.starttls()
        email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        file.write('Logged in successfully.\n')
        email_server.ehlo()
        recipient_list = [to, ]
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (settings.EMAIL_HOST_USER, ", ".join(recipient_list), subject, message)
        email_server.sendmail(settings.EMAIL_HOST_USER, recipient_list, message)
        email_server.close()
        file.write('Email sent successfully.\n')
    except Exception as error:
        print(error)
        file.write('Error thrown.\n')
        file.write('Error details => ' + str(error) + '\n')
    file.close()

