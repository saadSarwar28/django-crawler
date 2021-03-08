# Generated by Django 3.1.6 on 2021-03-01 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0005_auto_20210301_0830'),
    ]

    operations = [
        migrations.CreateModel(
            name='FetchDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(blank=True, max_length=100, null=True)),
                ('day', models.IntegerField(default=0)),
            ],
        ),
    ]
