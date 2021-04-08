from django.urls import path

from . import views

urlpatterns = [
    path('uae', views.crawl_uae, name='crawl both sites'),
    path('ksa', views.crawl_ksa, name='crawl ksa site'),
    path('create/fetch/day', views.create_fetch_day_, name='create fetch day'),
    path('save/remaining/days', views.save_remaining_products, name='save remaining products days'),
    path('delete', views.delete_files_from_google, name='delete files from google drive'),
    path('upload', views.upload_files_to_google, name='upload files to google drive'),
    path('move', views.move_files_to_backup, name='move files to backup folder'),
    # test functions
    path('save/remaining/days/by/category', views.save_remaining_products_by_category, name='save remaining products days'),
    path('write', views.write_data, name='write data to files'),
    path('send/email', views.send_email_gmail, name='send email'),
    path('get', views.get_input_files, name='get input files'),
    path('get/fetch/day', views.get_fetch_day, name='get fetch days count'),
    path('correct', views.correction_countries, name='country correction'),
    path('rectify/sold/quantity', views.rectify_sold_quantities, name='sold quantities calculation'),
]
