# Generated by Django 3.1.6 on 2021-03-02 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0009_auto_20210302_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='day',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='buy_box_Price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='total_inventory',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
