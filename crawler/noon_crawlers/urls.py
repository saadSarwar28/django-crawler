from django.urls import path

from . import views

urlpatterns = [
    path('noon', views.start_noon_crawling, name='start_crawling'),
    path('write', views.write_data, name='start_crawling')
]
