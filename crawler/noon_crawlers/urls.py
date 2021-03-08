from django.urls import path

from . import views

urlpatterns = [
    path('noon', views.start_noon_crawling, name='start_crawling'),
    path('write', views.write_data, name='start_crawling'),
    path('upload', views.upload_files_to_google, name='start_crawling'),
    path('delete', views.delete_files_from_google, name='start_crawling'),
]
