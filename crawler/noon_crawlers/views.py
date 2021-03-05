import threading
from .models import *
from django.http import HttpResponse
from django.shortcuts import render
from .selenium_crawler import start_crawling
from .selenium_crawler import write_data_to_file
# Create your views here.


def start_noon_crawling(request):
    start_crawling()
    return HttpResponse()


def write_data(request):
    categories = Product.objects.values('category').distinct()
    for category in categories:
        write_data_to_file(category['category'], 'UAE')
    return HttpResponse()
