from django.urls import path
from .views import *


app_name = 'sitepages'


urlpatterns = [
    path('',Home,name='homepage'),
    path('about/',About,name='aboutpage'),
    path('service/',Service,name='servicepage'),
    path('cars/',Car,name='carpage'),
    path('cars-detail/<str:car_slug>/',Car_details,name='car_details'),
    path('contact/',Contact,name='contactpage'),
    path('search_cars/',car_search, name='search-cars'),
    path('cars/<str:brand_name>/', cars_by_brand, name='cars_by_brand'),
    # path('cars/<int:car_id>/check_availability/', check_availability, name='check_availability'),
    path('booking/', booking, name='booking'),
    path('booking/confirm/',confirm_booking, name='confirm_booking'),

    # URL for payment methods (e.g., PayPal, bank transfer)
    path('payment/stripe/', stripe_payment, name='stripe_payment'),
    path('payment/success/', payment_success, name='payment_success'),  # Add your success view
    path('payment/success/stripe', payment_success_stripe, name='payment_success_stripe'),  # Add your success view
    path('payment/cancel/', payment_cancel, name='payment_cancel'),  
    path('payment/paypal/', show_paypal_payment, name='show_paypal_payment'),
    path('payment/paypal/submit/', paypal_payment, name='paypal_payment'), 
    path('booking-history/', booking_history, name='booking_history'),
]
