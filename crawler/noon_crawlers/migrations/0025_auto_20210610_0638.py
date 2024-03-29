# Generated by Django 3.1.6 on 2021-06-10 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0024_auto_20210503_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='updated_today',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='month',
            field=models.CharField(default='June', max_length=25),
        ),
        migrations.AlterField(
            model_name='day',
            name='month',
            field=models.CharField(default='June', max_length=25),
        ),
    ]
