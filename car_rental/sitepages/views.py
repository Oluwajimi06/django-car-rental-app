from django.shortcuts import render,redirect,get_object_or_404
from .models import Cars, Location, Booking
from datetime import datetime, timedelta
import random
from django.db import models

from django.http import HttpResponse

# from datetime import datetime, timedelta
from django.contrib import messages
from django.utils import timezone  # For timezone handling

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from decimal import Decimal
import stripe
from django.conf import settings

from django.views.decorators.http import require_POST
from paypalrestsdk import Payment  # Import PayPal SDK
import paypalrestsdk
# from paypalrestsdk import Payment

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.
def Home(request):
    cars = list(Cars.objects.all())
    random.shuffle(cars)  # Shuffle the list of cars
    six_cars = cars[:6]
    
    data = {'ptitle' : 'ROYAL CARS - Home','cars': six_cars}

    return render(request,'sitepages/index.html',data)


def About(request):
    data = {'ptitle' : 'ROYAL CARS - About'}

    return render(request,'sitepages/about.html',data)

def Service(request):
    data = {'ptitle' : 'ROYAL CARS - Service'}

    return render(request,'sitepages/service.html',data)

def Car(request):
    cars = list(Cars.objects.all())
    random.shuffle(cars)  # Shuffle the list of cars
    data = {'ptitle' : 'ROYAL CARS - Cars','cars': cars}

    return render(request,'sitepages/car.html',data)



def Contact(request):
    if request.method == 'POST':
        # Retrieve form data from POST request
        name = request.POST.get('fname')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate the form (you can add more validation as needed)
        if name and email and subject and message:
            # Example: Send an email to site admin (adjust settings accordingly)
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',  # Email subject
                    message=f'Name: {name}\nEmail: {email}\nMessage: {message}',  # Email body
                    from_email=email,  # Sender (you should define this in settings)
                    recipient_list=[settings.EMAIL_HOST_USER],  # Recipient(s), set your admin email in settings
                    fail_silently=False,  # Optionally, raise errors on failure
                )
                # Show a success message to the user
                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            except Exception as e:
                messages.error(request, f'Error sending your message: {e}')
        else:
            # If the form is incomplete
            messages.error(request, 'Please fill in all the fields.')

    # If the request is GET or the form was not filled in correctly, render the contact page
    data = {'ptitle': 'ROYAL CARS - Contact'}
    return render(request, 'sitepages/contact.html', data)

# def Contact(request):
#     if request.method == 'POST':
#         name = request.post.get('name')
#         email = request.post.get('email')
#         subject = request.post.get('subject')
#         message = request.post.get('message')

#         send_mail(
#             f"Contact Form Submission from {name}",
#             f"Message: {message}\n\nFrom: {name}, Email: {email}",
#             email,  # From email
#             ['admin@example.com'],  # Admin email to receive the message
#         )

#         messages.success(request, 'Your message has been sent successfully!')


#     data = {'ptitle' : 'ROYAL CARS - Contact'}

#     return render(request,'sitepages/contact.html',data)





def Car_details(request, car_slug):
    # Get the car object using the slug (ensure the slug is unique)
    car = get_object_or_404(Cars, slug=car_slug)
    locations = Location.objects.all()  # Fetch all available locations
    related_cars = Cars.objects.exclude(id=car.id)  # Fetch all cars excluding the current one

    ptitle = f"ROYAL CARS - {car.name} Details"

    if request.method == 'POST':
        # Get form data
        pickup_location_id = request.POST.get('pickup_location')
        drop_location_id = request.POST.get('drop_location')
        pickup_date = request.POST.get('pickup_date')  # Format: YYYY-MM-DD
        dropoff_date = request.POST.get('dropoff_date')  # Format: YYYY-MM-DD

        # Validate that all fields are filled
        if not (pickup_location_id and drop_location_id and pickup_date and dropoff_date):
            messages.error(request, 'All fields are required.')
            return render(request, 'sitepages/detail.html', {
                'car': car,
                'locations': locations,
                'related_cars': related_cars,
                'ptitle': ptitle  # Add page title here
            })

        # Try to combine the dates into timezone-aware datetime objects
        try:
            pickup_datetime = timezone.make_aware(datetime.strptime(pickup_date, '%Y-%m-%d'))
            dropoff_datetime = timezone.make_aware(datetime.strptime(dropoff_date, '%Y-%m-%d'))
        except ValueError:
            messages.error(request, 'Invalid date format. Please try again.')
            return render(request, 'sitepages/detail.html', {
                'car': car,
                'locations': locations,
                'related_cars': related_cars,
                'ptitle': ptitle  # Add page title here
            })

        # Get the current time for comparison (timezone-aware)
        now = timezone.now()

        # Check if the pickup date is in the past
        # Change the condition to allow today's date
        if pickup_datetime.date() < now.date():
            messages.error(request, 'Pickup date cannot be in the past.')
            return render(request, 'sitepages/detail.html', {
                'car': car,
                'locations': locations,
                'related_cars': related_cars,
                'ptitle': ptitle  # Add page title here
            })

        # Check if the drop-off date is after the pickup date
        if dropoff_datetime <= pickup_datetime:
            messages.error(request, 'Drop-off date must be after the pickup date.')
            return render(request, 'sitepages/detail.html', {
                'car': car,
                'locations': locations,
                'related_cars': related_cars,
                'ptitle': ptitle  # Add page title here
            })

        # Check if the car is available for the selected dates
        if car.is_available_for_dates(pickup_datetime.date(), dropoff_datetime.date()):
            # Store the booking details in session
            request.session['booking_details'] = {
                'pickup_location': pickup_location_id,
                'drop_location': drop_location_id,
                'pickup_datetime': pickup_datetime.strftime('%Y-%m-%d'),
                'dropoff_datetime': dropoff_datetime.strftime('%Y-%m-%d'),
                'car_id': car.id,
            }
            # Redirect to booking page
            return redirect('sitepages:booking')
        else:
            # If not available, show an error
            messages.error(request, f'Sorry, {car.name} is not available for the selected dates.')
            return render(request, 'sitepages/detail.html', {
                'car': car,
                'locations': locations,
                'related_cars': related_cars,
                'ptitle': ptitle  # Add page title here
            })

    # If it's a GET request, show the car details form
    return render(request, 'sitepages/detail.html', {
        'car': car,
        'locations': locations,
        'related_cars': related_cars,
        'ptitle': ptitle  # Add page title here
    })





def car_search(request):
    # Get search parameters
    car_name = request.GET.get('car_name', '')
    brand = request.GET.get('brand', '')
    transmission = request.GET.get('transmission', '')

    # Filter cars based on the search parameters
    cars = Cars.objects.all()

    if car_name:
        cars = cars.filter(name__icontains=car_name)
    if brand:
        cars = cars.filter(brand=brand)
    if transmission:
        cars = cars.filter(transmission=transmission)

    # Render results in the results template

    data = {'ptitle' : 'ROYAL CARS - Search Results','cars': cars}
    return render(request, 'sitepages/car_results.html', data)




def cars_by_brand(request, brand_name):
    cars = Cars.objects.filter(brand=brand_name, is_available=True)
    data = {'ptitle': 'ROYAL CARS - Car Brands'}

    # Combine 'data' dictionary with the context
    context = {
        'brand_name': brand_name,
        'cars': cars,
    }
    context.update(data)  # Merging the data dictionary with the existing context

    return render(request, 'sitepages/cars_by_brand.html', context)






@login_required
def booking(request):
    # Retrieve booking details from the session
    booking_details = request.session.get('booking_details')
    
    if not booking_details:
        messages.error(request, 'No booking details found. Please try again.')
        return redirect('sitepages:homepage')  # Redirect to car list or home page if no booking details

    # Fetch the car and locations from the IDs stored in session
    car = get_object_or_404(Cars, id=booking_details['car_id'])
    pickup_location = get_object_or_404(Location, id=booking_details['pickup_location'])
    drop_location = get_object_or_404(Location, id=booking_details['drop_location'])

    # Parse the datetime strings back to datetime objects
    try:
        # Adjusting to match the new format from Car_details (only date part)
        pickup_datetime = datetime.strptime(booking_details['pickup_datetime'], '%Y-%m-%d')
        dropoff_datetime = datetime.strptime(booking_details['dropoff_datetime'], '%Y-%m-%d')
    except ValueError:
        messages.error(request, 'Invalid date format. Please try again.')
        return redirect('sitepages:car_details', car_slug=car.slug)  # Redirect back to the car detail page

    # Calculate the number of rental days, including same-day rental scenarios
    rental_duration = dropoff_datetime - pickup_datetime
    rental_days = rental_duration.days + (1 if rental_duration.seconds > 0 else 0)  # Add 1 day if it's a partial day rental

    if rental_days <= 0:
        messages.error(request, 'Invalid rental period. Drop-off date must be after pickup date.')
        return redirect('sitepages:car_details', car_slug=car.slug)

    # Calculate total cost based on daily rate and number of rental days
    total_cost = rental_days * car.daily_rate


    

    # Render the booking page with all relevant booking details
    return render(request, 'sitepages/booking.html', {
        'car': car,
        'pickup_location': pickup_location,
        'drop_location': drop_location,
        'pickup_datetime': pickup_datetime,
        'dropoff_datetime': dropoff_datetime,
        'total_cost': total_cost,
        'rental_days': rental_days,  # Pass rental days if needed in the template
    })




def confirm_booking(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        special_request = request.POST.get('special_request')
        payment_method = request.POST.get('payment_method')
        total_cost = request.POST.get('total_cost')  # Retrieve total cost from POST data

        # Retrieve booking details from session
        booking_details = request.session.get('booking_details')
        if not booking_details:
            messages.error(request, 'No booking details found. Please try again.')
            return redirect('sitepages:car_details')

        # Validate and process booking details
        car = get_object_or_404(Cars, id=booking_details['car_id'])
        pickup_location = get_object_or_404(Location, id=booking_details['pickup_location'])
        drop_location = get_object_or_404(Location, id=booking_details['drop_location'])

        # Convert dates stored in session to timezone-aware datetime objects
        try:
            pickup_datetime = timezone.make_aware(datetime.strptime(booking_details['pickup_datetime'], '%Y-%m-%d'))
            dropoff_datetime = timezone.make_aware(datetime.strptime(booking_details['dropoff_datetime'], '%Y-%m-%d'))
        except ValueError:
            messages.error(request, 'Invalid date format. Please try again.')
            return redirect('sitepages:car_details', car_slug=car.slug)

        # Calculate rental days
        rental_days = (dropoff_datetime - pickup_datetime).days + 1  # Ensure at least one day rental
        if rental_days <= 0:
            messages.error(request, 'Invalid rental period. Drop-off date must be after pickup date.')
            return redirect('sitepages:car_details', car_slug=car.slug)

        # Ensure total cost is provided and valid
        if not total_cost:
            messages.error(request, 'Total cost not found. Please recheck your booking details.')
            return redirect('sitepages:car_details', car_slug=car.slug)

        try:
            total_cost_float = float(total_cost)
        except ValueError:
            messages.error(request, 'Invalid total cost value. Please recheck your booking details.')
            return redirect('sitepages:car_details', car_slug=car.slug)

        # Store booking details in session for later confirmation after payment
        request.session['pending_booking'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'mobile_number': mobile_number,
            'special_request': special_request,
            'car_id': car.id,
            'pickup_location_id': pickup_location.id,
            'drop_location_id': drop_location.id,
            'pickup_datetime': pickup_datetime.isoformat(),
            'dropoff_datetime': dropoff_datetime.isoformat(),
            'rental_days': rental_days,
            'total_cost': total_cost_float,  # Store as float
            'payment_method': payment_method,
        }

        # Redirect based on payment method
        payment_redirects = {
            'stripe': '/payment/stripe/',
            'paypal': '/payment/paypal/',
        }
        if payment_method in payment_redirects:
            return redirect(payment_redirects[payment_method])
        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('sitepages:booking')

    return redirect('sitepages:booking')  # Redirect if not a POST request






def stripe_payment(request):
    # Retrieve pending booking from session
    pending_booking = request.session.get('pending_booking')
    if not pending_booking:
        messages.error(request, 'No pending booking found.')
        return redirect('sitepages:booking')

    # Set your secret key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Retrieve the car using the car_id from the session
    car = get_object_or_404(Cars, id=pending_booking['car_id'])

    # Create a new Stripe Checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],  # Accept card payments
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',  # Set your currency
                        'product_data': {
                            'name': f"Car Rental: {car.name}",  # Include car details
                            'description': f"Rental from {pending_booking['pickup_datetime']} to {pending_booking['dropoff_datetime']}",
                        },
                        'unit_amount': int(pending_booking['total_cost'] * 100),  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/payment/success/stripe'),  # Absolute URL for success
            cancel_url=request.build_absolute_uri('/payment/cancel/'),  # Absolute URL for cancel
        )
    except Exception as e:
        messages.error(request, f"An error occurred while creating the payment session: {str(e)}")
        return redirect('sitepages:booking')  # Redirect to booking if an error occurs

    # Redirect to Stripe Checkout
    return redirect(session.url, code=303)  # Use code=303 for a 303 redirect




def payment_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, 'Payment information is missing.')
        return redirect('sitepages:booking')

    # Retrieve pending booking from the session
    pending_booking = request.session.get('pending_booking')
    if not pending_booking:
        messages.error(request, 'No pending booking found.')
        return redirect('sitepages:booking')

    # Verify the payment with PayPal
    payment = Payment.find(payment_id)

    if payment:
        # Execute the payment
        if payment.execute({"payer_id": payer_id}):
            # The payment was successfully completed
            messages.success(request, 'Payment was successful!')

            # Create a new booking instance
            booking = Booking(
                first_name=pending_booking['first_name'],
                last_name=pending_booking['last_name'],
                email=pending_booking['email'],
                mobile_number=pending_booking['mobile_number'],
                special_request=pending_booking['special_request'],
                car_id=pending_booking['car_id'],  # Assuming this is a foreign key or ID reference
                pickup_location_id=pending_booking['pickup_location_id'],
                drop_location_id=pending_booking['drop_location_id'],
                pickup_datetime=pending_booking['pickup_datetime'],
                dropoff_datetime=pending_booking['dropoff_datetime'],
                rental_days=pending_booking['rental_days'],
                total_cost=pending_booking['total_cost'],
                payment_method=pending_booking['payment_method'],
            )

            # Assign the logged-in user to the booking if they are authenticated
            if request.user.is_authenticated:
                booking.user = request.user  # Assign the logged-in user to the booking

            # Save the booking to the database
            try:
                booking.save()
            except Exception as e:
                messages.error(request, f"An error occurred while saving the booking: {str(e)}")
                return redirect('sitepages:booking')

            # Clear all session data related to the booking
            del request.session['pending_booking']
            # Prepare email content
             # Prepare email content for the user
            subject_user = 'Your Booking Confirmation'
            html_message_user = render_to_string('emails/booking_confirmation_user.html', {'booking': booking})
            plain_message_user = strip_tags(html_message_user)

            # Prepare email content for the owner
            subject_owner = 'New Booking Notification'
            html_message_owner = render_to_string('emails/booking_confirmation_owner.html', {'booking': booking})
            plain_message_owner = strip_tags(html_message_owner)

            # Send email to user (to console)
            send_mail(subject_user, plain_message_user,settings.EMAIL_HOST_USER, [booking.email], html_message=html_message_user)
            # Send email to owner (to console)
            send_mail(subject_owner, plain_message_owner,settings.EMAIL_HOST_USER, ['obadimejiayomide9@gmail.com'], html_message=html_message_owner)



            # Redirect to a confirmation page or render a success template
            messages.success(request, 'Your booking has been successfully confirmed!')
            return render(request, 'payment/success.html')
        else:
            # The payment execution failed
            messages.error(request, 'Payment could not be completed.')
            return redirect('sitepages:booking')
    else:
        # The payment could not be found
        messages.error(request, 'Payment not found.')
        return redirect('sitepages:booking')


def payment_success_stripe(request):
    # Retrieve pending booking from the session
    pending_booking = request.session.get('pending_booking')
    if not pending_booking:
        messages.error(request, 'No pending booking found.')
        return redirect('sitepages:booking')

    # Create a new booking instance
    booking = Booking(
        first_name=pending_booking['first_name'],
        last_name=pending_booking['last_name'],
        email=pending_booking['email'],
        mobile_number=pending_booking['mobile_number'],
        special_request=pending_booking['special_request'],
        car_id=pending_booking['car_id'],  # Assuming this is a foreign key or ID reference
        pickup_location_id=pending_booking['pickup_location_id'],
        drop_location_id=pending_booking['drop_location_id'],
        pickup_datetime=pending_booking['pickup_datetime'],
        dropoff_datetime=pending_booking['dropoff_datetime'],
        rental_days=pending_booking['rental_days'],
        total_cost=pending_booking['total_cost'],
        payment_method=pending_booking['payment_method'],
    )

    # Assign the logged-in user to the booking if they are authenticated
    if request.user.is_authenticated:
        booking.user = request.user  # Assign the logged-in user to the booking

    # Save the booking to the database
    try:
        booking.save()
    except Exception as e:
        messages.error(request, f"An error occurred while saving the booking: {str(e)}")
        return redirect('sitepages:booking')  # Redirect if there's an error saving

    # Clear all session data related to the booking
    del request.session['pending_booking']

     # Prepare email content for the user
    subject_user = 'Your Booking Confirmation'
    html_message_user = render_to_string('emails/booking_confirmation_user.html', {'booking': booking})
    plain_message_user = strip_tags(html_message_user)

    # Prepare email content for the owner
    subject_owner = 'New Booking Notification'
    html_message_owner = render_to_string('emails/booking_confirmation_owner.html', {'booking': booking})
    plain_message_owner = strip_tags(html_message_owner)

    # Send email to user (to console)
    send_mail(subject_user, plain_message_user,settings.EMAIL_HOST_USER, [booking.email], html_message=html_message_user)
    # Send email to owner (to console)
    send_mail(subject_owner, plain_message_owner,settings.EMAIL_HOST_USER, ['obadimejiayomide9@gmail.com'], html_message=html_message_owner)



    # Redirect to a confirmation page or render a success template
    messages.success(request, 'Your booking has been successfully confirmed!')
    return render(request, 'payment/success.html')  # Create a success.html template

def payment_cancel(request):
    # Clear the pending booking from the session
    if 'pending_booking' in request.session:
        del request.session['pending_booking']
    
    # Optionally, add a message indicating the cancellation
    messages.info(request, 'Your payment has been canceled. You can try again or make another booking.')

    # Render the cancel template
    return render(request, 'payment/cancel.html')  # Create a cancel.html template



def show_paypal_payment(request):
    # Retrieve pending booking from session
    pending_booking = request.session.get('pending_booking')
    if not pending_booking:
        messages.error(request, 'No pending booking found.')
        return redirect('sitepages:booking')

    # Retrieve the car using the car_id from the session
    car = get_object_or_404(Cars, id=pending_booking['car_id'])

    # Prepare the context for the template
    context = {
        'car_name': car.name,
        'pickup_datetime': pending_booking['pickup_datetime'],
        'dropoff_datetime': pending_booking['dropoff_datetime'],
        'total_cost': f"{pending_booking['total_cost']:.2f}",
        'currency': 'USD',  # This is fine to include for reference in the template
    }

    # Render the paypal_payment.html template with booking details
    return render(request, 'payment/paypal_payment.html', context)



@require_POST
def paypal_payment(request):
    # Retrieve pending booking from session
    pending_booking = request.session.get('pending_booking')
    if not pending_booking:
        messages.error(request, 'No pending booking found.')
        return redirect('sitepages:booking')

    # Retrieve the car using the car_id from the session
    car = get_object_or_404(Cars, id=pending_booking['car_id'])
    
    # Debugging: Log the pending booking details
    print("Pending booking details:", pending_booking)
    print(f"Total cost before payment creation: {pending_booking['total_cost']:.2f}")

    # Create a new PayPal payment
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/payment/success/'),  # URL for successful payment
            "cancel_url": request.build_absolute_uri('/payment/cancel/')  # URL for cancelled payment
        },
        "transactions": [{
            "amount": {
                "total": f"{pending_booking['total_cost']:.2f}",  # Amount in dollars
                "currency": "USD"  # Set your currency
            },
            "description": f"Car Rental: {car.name} from {pending_booking['pickup_datetime']} to {pending_booking['dropoff_datetime']}"
        }]
    })

    # Log payment details before creation
    print("Payment details before creation:", payment.to_dict())

    # Create the payment
    if payment.create():
        # Payment creation successful
        print("Payment created successfully.")
        # Log PayPal redirect URL for approval
        for link in payment.links:
            if link.rel == "approval_url":
                print("Redirecting to PayPal for approval:", link.href)
                return redirect(link.href)  # Redirect to PayPal for approval
    else:
        # Payment creation failed
        print("Payment creation failed:", payment.error)
        messages.error(request, f"An error occurred while creating the payment: {payment.error}")
        return redirect('sitepages:booking')  # Redirect to booking if an error occurs



def booking_history(request):
    # Get all bookings for the currently logged-in user
    bookings = Booking.objects.filter(user=request.user).order_by('-pickup_datetime')

    context = {
        'bookings': bookings,
    }

    return render(request, 'sitepages/booking_history.html', context)
