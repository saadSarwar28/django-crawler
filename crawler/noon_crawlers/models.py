import datetime

from django.db import models

# Create your models here.


class FetchDay(models.Model):
    month = models.CharField(max_length=100, null=True, blank=True)
    day = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    country = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=1000, null=True, blank=True)
    sku = models.CharField(max_length=250, null=True, blank=True)
    product_title = models.CharField(max_length=1000, null=True, blank=True)
    listing_url = models.CharField(max_length=1000, null=True, blank=True)
    image_url = models.CharField(max_length=1000, null=True, blank=True)
    brand = models.CharField(max_length=1000, null=True, blank=True)
    report_date_time = models.CharField(max_length=250, null=True, blank=True)
    no_of_sellers = models.IntegerField(null=True, blank=True)
    no_of_fbn_sellers = models.IntegerField(default=0, null=True, blank=True)
    buy_box_seller = models.CharField(max_length=250, null=True, blank=True)
    buy_box_Price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # now actually latest buy box inventory
    total_inventory = models.CharField(max_length=100, null=True, blank=True)
    sold_quantity_last_day = models.IntegerField(null=True, blank=True)
    sold_quantity_last_7_day = models.IntegerField(null=True, blank=True)
    sold_quantity_last_30_day = models.IntegerField(null=True, blank=True)
    # listing_with_incorrect_inventory = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_today = models.BooleanField(default=False)

    def __str__(self):
        return self.sku


class Day(models.Model):
    day_count = models.IntegerField(default=0)
    month = models.CharField(max_length=25, default=datetime.datetime.now().date().strftime('%B'))
    day = models.DateField(null=True, blank=True)
    sold_quantity = models.IntegerField(default=0, null=True, blank=True)
    inventory = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class ProxyPorts(models.Model):
    port_number = models.IntegerField()
    site = models.CharField(max_length=25, null=True, blank=True)
    starting_bandwidth = models.DecimalField(max_digits=16, decimal_places=8, default=0.0)
    ending_bandwidth = models.DecimalField(max_digits=16, decimal_places=8, default=0.0)
    bandwidth_utilized = models.DecimalField(max_digits=16, decimal_places=8, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FilesToDelete(models.Model):
    file_id = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


class Category(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True)
    month = models.CharField(max_length=25, default=datetime.datetime.now().date().strftime('%B'))
    country = models.CharField(max_length=200, null=True, blank=True)
    fetch_day_count = models.IntegerField(default=0, null=True, blank=True)
    num_of_pages_scraped = models.IntegerField(default=0)
    num_of_skus = models.IntegerField(default=0)
    fully_scraped = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

