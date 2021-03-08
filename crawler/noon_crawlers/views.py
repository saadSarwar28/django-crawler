import threading
from .models import *
from django.http import HttpResponse
from django.shortcuts import render
from .selenium_crawler import start_crawling
from .selenium_crawler import write_data_to_file
from .selenium_crawler import upload_files_to_google_drive
from .selenium_crawler import delete_previous_files_from_google_drive
# Create your views here.


def start_noon_crawling(request):
    start_crawling()
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

