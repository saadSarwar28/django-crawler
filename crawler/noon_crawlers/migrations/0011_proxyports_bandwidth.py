# Generated by Django 3.1.6 on 2021-03-02 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0010_auto_20210303_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxyports',
            name='bandwidth',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=10),
        ),
    ]
