# Generated by Django 5.1.2 on 2024-10-16 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0004_cars_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cars',
            name='slug',
            field=models.SlugField(blank=True, default='', unique=True),
        ),
    ]
