# Generated by Django 5.1 on 2024-08-29 20:34
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post_tags'),
    ]

    operations = [
        TrigramExtension()
    ]
