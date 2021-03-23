import threading
from .models import *
from django.http import HttpResponse
from django.shortcuts import render
from .selenium_crawler import *
# Create your views here.


def crawl_uae(request):
    start_crawling('UAE', number_of_pages=2)
    return HttpResponse()


def crawl_ksa(request):
    start_crawling('KSA', number_of_pages=2)
    return HttpResponse()


def create_fetch_day_(request):
    create_fetch_day()
    return HttpResponse()


def get_fetch_day(request):
    print(get_fetch_day_count())
    return HttpResponse()


def save_remaining_products(request):
    save_remaining_products_days()
    return HttpResponse()


def send_email_gmail(request):
    send_email('KSA', 10, 4)
    return HttpResponse()


def write_data(request):
    categories = Product.objects.values('category').distinct()
    for category in categories:
        write_data_to_file(category['category'], 'UAE')
    return HttpResponse()


def upload_files_to_google(request):
    upload_files_to_google_drive('accesories and supplies-05.csv')
    return HttpResponse()


def delete_files_from_google(request):
    delete_previous_files_from_google_drive()
    return HttpResponse()


def get_input_files(request):
    print(get_input_file('UAE'))
    return HttpResponse()


