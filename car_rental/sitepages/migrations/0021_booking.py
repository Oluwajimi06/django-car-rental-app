# Generated by Django 5.1.2 on 2024-10-19 12:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0020_delete_carbooking'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_datetime', models.DateTimeField()),
                ('dropoff_datetime', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitepages.cars')),
                ('drop_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drop_bookings', to='sitepages.location')),
                ('pickup_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pickup_bookings', to='sitepages.location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
