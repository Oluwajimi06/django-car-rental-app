# Generated by Django 5.1.2 on 2024-10-18 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0019_remove_location_is_active_carbooking_delete_booking_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CarBooking',
        ),
    ]
