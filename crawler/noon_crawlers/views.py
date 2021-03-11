import threading
from .models import *
from django.http import HttpResponse
from django.shortcuts import render
from .selenium_crawler import *
# Create your views here.


def crawl_uae(request):
    start_crawling('UAE')
    return HttpResponse()


def crawl_ksa(request):
    start_crawling('KSA')
    return HttpResponse()


def save_remaining_products(request):
    save_remaining_products_days(2)
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
    print(get_input_file('KSA'))
    return HttpResponse()


