# Generated by Django 5.1.2 on 2024-10-16 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0003_rename_car_cars'),
    ]

    operations = [
        migrations.AddField(
            model_name='cars',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]