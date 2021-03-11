from django.urls import path

from . import views

urlpatterns = [
    path('uae', views.crawl_uae, name='crawl uae site'),
    path('ksa', views.crawl_ksa, name='crawl ksa site'),
    # test functions
    path('write', views.write_data, name='write data to files'),
    path('save/remaining/days', views.save_remaining_products, name='save remaining products days'),
    path('send/email', views.send_email_gmail, name='send email'),
    path('get', views.get_input_files, name='get input files'),
    path('upload', views.upload_files_to_google, name='upload files to google drive'),
    path('delete', views.delete_files_from_google, name='delete files from google drive'),
]
