# Generated by Django 5.1.2 on 2024-10-19 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0022_booking_email_booking_first_name_booking_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='rental_days',
            field=models.IntegerField(default=0),
        ),
    ]