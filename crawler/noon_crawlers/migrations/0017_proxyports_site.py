# Generated by Django 3.1.6 on 2021-03-12 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0016_filestodelete'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxyports',
            name='site',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
