from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone


# Create your models here.



# Create your models here.

class Cars(models.Model):
    # Choices for car brands
    BRAND_CHOICES = [
        ('Volkswagen', 'Volkswagen'),
        ('BMW', 'BMW'),
        ('NISSAN', 'NISSAN'),
        ('Audi', 'Audi'),
        ('Porsche', 'Porsche'),
        ('Ford', 'Ford'),
        ('Nord Motion', 'Nord Motion'),
        ('Mercedez Benz', 'Mercedez Benz'),
        ('Toyota', 'Toyota'),
    ]
    
    # Choices for transmission types
    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]
    
    # Model fields
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)  # Car brand
    name = models.CharField(max_length=100)  # Car model name, e.g., "Mercedes Benz R3"
    model_year = models.IntegerField()  # Model year, e.g., 2015
    transmission = models.CharField(max_length=50, choices=TRANSMISSION_CHOICES)  # Transmission type
    mileage = models.CharField(max_length=50)  # Mileage, e.g., "25K"
    fuel_efficiency = models.CharField(max_length=50)  # Fuel efficiency, e.g., "20km/liter"
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)  # Daily rental rate, e.g., 99.00
    gps_navigation = models.BooleanField(default=False)  # GPS navigation feature
    is_available = models.BooleanField(default=True)  # Availability of the car for booking
    image = models.ImageField(upload_to='cars/')  # Car image
    description = models.TextField()  # Long description of the car
    slug = models.SlugField(unique=True, blank=True)  # Slug for URL

    def save(self, *args, **kwargs):
        # Generate the slug from the car name if not already set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.brand} {self.name} ({self.model_year})'

    def is_available_for_dates(self, pickup_date, dropoff_date):
        """
        Check if the car is available for the given date range.
        This method checks for overlapping bookings without considering the time of day.
        """
        existing_bookings = Booking.objects.filter(
            car=self,
            pickup_datetime__date__lte=dropoff_date,  # Check if the pickup date is before or on the dropoff date
            dropoff_datetime__date__gte=pickup_date     # Check if the dropoff date is after or on the pickup date
        )
        return existing_bookings.count() == 0  # If no bookings overlap, the car is available


# class Cars(models.Model):
#     # Choices for car brands
#     BRAND_CHOICES = [
#         ('Volkswagen', 'Volkswagen'),
#         ('BMW', 'BMW'),
#         ('NISSAN', 'NISSAN'),
#         ('Audi', 'Audi'),
#         ('Porsche', 'Porsche'),
#         ('Ford', 'Ford'),
#         ('Nord Motion', 'Nord Motion'),
#         ('Mercedez Benz', 'Mercedez Benz'),
#         ('Toyota', 'Toyota'),
#     ]
    
#     # Choices for transmission types
#     TRANSMISSION_CHOICES = [
#         ('Automatic', 'Automatic'),
#         ('Manual', 'Manual'),
#     ]
    
#     # Model fields
#     brand = models.CharField(max_length=50, choices=BRAND_CHOICES)  # Car brand
#     name = models.CharField(max_length=100)  # Car model name, e.g., "Mercedes Benz R3"
#     model_year = models.IntegerField()  # Model year, e.g., 2015
#     transmission = models.CharField(max_length=50, choices=TRANSMISSION_CHOICES)  # Transmission type
#     mileage = models.CharField(max_length=50)  # Mileage, e.g., "25K"
#     fuel_efficiency = models.CharField(max_length=50)  # Fuel efficiency, e.g., "20km/liter"
#     daily_rate = models.DecimalField(max_digits=10, decimal_places=2)  # Daily rental rate, e.g., 99.00
#     gps_navigation = models.BooleanField(default=False)  # GPS navigation feature
#     is_available = models.BooleanField(default=True)  # Availability of the car for booking
#     image = models.ImageField(upload_to='cars/')  # Car image
#     description = models.TextField()  # Long description of the car
#     slug = models.SlugField(unique=True, blank=True)  # Slug for URL

#     def save(self, *args, **kwargs):
#         # Generate the slug from the car name if not already set
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f'{self.brand} {self.name} ({self.model_year})'

#     def is_available_for(self, pickup_datetime, dropoff_datetime):
#         # Check for overlapping bookings
#         existing_bookings = Booking.objects.filter(
#             car=self,
#             pickup_datetime__lt=dropoff_datetime,
#             dropoff_datetime__gt=pickup_datetime  # Ensure dropoff_datetime is also considered
#         )
#         return existing_bookings.count() == 0  # If no bookings overlap, the car is available



        





class CarImage(models.Model):
    car = models.ForeignKey(Cars, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')

    def __str__(self):
        return f'Image of {self.car.name}'



class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name




class Booking(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    car = models.ForeignKey(Cars, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, related_name='pickup_bookings', on_delete=models.CASCADE)
    drop_location = models.ForeignKey(Location, related_name='drop_bookings', on_delete=models.CASCADE)
    pickup_datetime = models.DateTimeField()
    dropoff_datetime = models.DateTimeField()  # Add drop-off datetime
    first_name = models.CharField(max_length=100,default='unknown')  # Add first name
    last_name = models.CharField(max_length=100,default='unknown')  # Add last name
    email = models.EmailField(default='default@example.com')  # Add email field
    mobile_number = models.CharField(max_length=15,default='unknown')  # Add mobile number
    special_request = models.TextField(blank=True, null=True)  # Optional field for special requests
    rental_days = models.IntegerField(default=0)  # Store rental days
    total_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)  # Store total cost of booking
    payment_method = models.CharField(max_length=50,default='unknown')  # Store the payment method (e.g., PayPal, Direct Check)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Booking for {self.car.name} by {self.user.username}'


# class CarBooking(models.Model):
#     car = models.ForeignKey('Car', on_delete=models.CASCADE)  # Assuming you have a Car model
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_bookings')
#     drop_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='drop_bookings')
#     pickup_date = models.DateField()
#     pickup_time = models.TimeField()
#     number_of_persons = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         # Add constraint to prevent overlapping bookings
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(number_of_persons__gte=1), 
#                 name='valid_number_of_persons'
#             )
#         ]

# class Booking(models.Model): 
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('active', 'Active'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ]

#     car = models.ForeignKey('Cars', on_delete=models.CASCADE, related_name='booking')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     pickup_time = models.TimeField()
#     return_time = models.TimeField()
#     booking_date = models.DateTimeField(auto_now_add=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     special_request = models.TextField(blank=True, null=True)  # New field for special requests
#     pickup_location = models.CharField(max_length=255,default='n/a')  # New field for pickup location
#     drop_location = models.CharField(max_length=255,default='n/a')  # New field for drop location
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
#     def __str__(self):
#         return f"Booking for {self.car} by {self.user.username}"
    
#     def calculate_total_amount(self):
#         # Calculate number of days
#         days = (self.end_date - self.start_date).days + 1
#         return self.car.daily_rate * days


# class Location(models.Model):
#     name = models.CharField(max_length=100)
#     address = models.TextField()
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name






# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional association with a user
#     car = models.ForeignKey(Cars, on_delete=models.CASCADE)  # Link to the selected car
#     first_name = models.CharField(max_length=50,default='NA')
#     last_name = models.CharField(max_length=50,default='NA')
#     email = models.EmailField(null=True, blank=True)
#     mobile_number = models.CharField(max_length=15,default='NA')
    
#     pickup_location = models.CharField(max_length=255)
#     dropoff_location = models.CharField(max_length=255)
    
#     pickup_date = models.DateTimeField()
#     dropoff_date = models.DateTimeField()

#     payment_method = models.CharField(max_length=50, default='Credit Card',)
    
#     total_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
#     is_paid = models.BooleanField(default=False)  # Track if the payment is completed
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Booking for {self.first_name} {self.last_name} - {self.car.make} {self.car.model}"


