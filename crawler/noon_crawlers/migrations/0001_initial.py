# Generated by Django 3.1.6 on 2021-02-16 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NOON_PRODUCT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category', models.CharField(blank=True, max_length=250, null=True)),
                ('NOON_SKU', models.CharField(blank=True, max_length=250, null=True)),
                ('Product_title', models.CharField(blank=True, max_length=250, null=True)),
                ('listing_url', models.CharField(blank=True, max_length=250, null=True)),
                ('image_url', models.CharField(blank=True, max_length=500, null=True)),
                ('Brand', models.CharField(blank=True, max_length=250, null=True)),
                ('REPORT_date_time', models.CharField(blank=True, max_length=250, null=True)),
                ('no_of_sellers', models.IntegerField(blank=True, null=True)),
                ('no_of_FBN_sellers', models.IntegerField(blank=True, null=True)),
                ('Buy_Box_seller', models.CharField(blank=True, max_length=250, null=True)),
                ('Buy_Box_Price', models.IntegerField(blank=True, null=True)),
                ('Total_inventory', models.IntegerField(blank=True, max_length=250, null=True)),
                ('Sold_quantity_last_day', models.IntegerField(blank=True, null=True)),
                ('sold_qantity_last_7_day', models.IntegerField(blank=True, null=True)),
                ('sold_quantity_last_30_day', models.IntegerField(blank=True, null=True)),
                ('listing_with_incorrect_inventory', models.CharField(blank=True, max_length=250, null=True)),
                ('day_31_inventory', models.IntegerField(blank=True, null=True)),
                ('day_30_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_30_inventory', models.IntegerField(blank=True, null=True)),
                ('day_29_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_29_inventory', models.IntegerField(blank=True, null=True)),
                ('day_28_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_28_inventory', models.IntegerField(blank=True, null=True)),
                ('day_27_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_27_inventory', models.IntegerField(blank=True, null=True)),
                ('day_26_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_26_inventory', models.IntegerField(blank=True, null=True)),
                ('day_25_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_25_inventory', models.IntegerField(blank=True, null=True)),
                ('day_24_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_24_inventory', models.IntegerField(blank=True, null=True)),
                ('day_23_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_23_inventory', models.IntegerField(blank=True, null=True)),
                ('day_22_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_22_inventory', models.IntegerField(blank=True, null=True)),
                ('day_21_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_21_inventory', models.IntegerField(blank=True, null=True)),
                ('day_20_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_20_inventory', models.IntegerField(blank=True, null=True)),
                ('day_19_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_19_inventory', models.IntegerField(blank=True, null=True)),
                ('day_18_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_18_inventory', models.IntegerField(blank=True, null=True)),
                ('day_17_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_17_inventory', models.IntegerField(blank=True, null=True)),
                ('day_16_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_16_inventory', models.IntegerField(blank=True, null=True)),
                ('day_15_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_15_inventory', models.IntegerField(blank=True, null=True)),
                ('day_14_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_14_inventory', models.IntegerField(blank=True, null=True)),
                ('day_13_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_13_inventory', models.IntegerField(blank=True, null=True)),
                ('day_12_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_12_inventory', models.IntegerField(blank=True, null=True)),
                ('day_11_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_11_inventory', models.IntegerField(blank=True, null=True)),
                ('day_10_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_10_inventory', models.IntegerField(blank=True, null=True)),
                ('day_9_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_9_inventory', models.IntegerField(blank=True, null=True)),
                ('day_8_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_8_inventory', models.IntegerField(blank=True, null=True)),
                ('day_7_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_7_inventory', models.IntegerField(blank=True, null=True)),
                ('day_6_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_6_inventory', models.IntegerField(blank=True, null=True)),
                ('day_5_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_5_inventory', models.IntegerField(blank=True, null=True)),
                ('day_4_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_4_inventory', models.IntegerField(blank=True, null=True)),
                ('day_3_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_3_inventory', models.IntegerField(blank=True, null=True)),
                ('day_2_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_2_inventory', models.IntegerField(blank=True, null=True)),
                ('day_1_sold_qty', models.IntegerField(blank=True, null=True)),
                ('day_1_inventory', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]