from django.contrib import admin
from .models import Cars, CarImage,Location,Booking

# Register your models here.
admin.site.register(Cars)
admin.site.register(CarImage)
admin.site.register(Location)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'pickup_location', 'drop_location', 'pickup_datetime', 'dropoff_datetime', 'created_at')
    search_fields = ('user__username', 'car__name', 'pickup_location__name', 'drop_location__name')
    list_filter = ('pickup_datetime', 'dropoff_datetime', 'pickup_location', 'drop_location')
# admin.site.register(CarBooking)
