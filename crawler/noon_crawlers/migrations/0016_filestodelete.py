# Generated by Django 3.1.6 on 2021-03-08 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noon_crawlers', '0015_auto_20210304_0413'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilesToDelete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
            ],
        ),
    ]
