# Generated by Django 3.1.6 on 2021-06-15 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0027_auto_20210616_0416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fetchday',
            name='created_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
