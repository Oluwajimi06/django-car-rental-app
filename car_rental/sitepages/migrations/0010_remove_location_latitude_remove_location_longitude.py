# Generated by Django 5.1.2 on 2024-10-17 00:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0009_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='longitude',
        ),
    ]
