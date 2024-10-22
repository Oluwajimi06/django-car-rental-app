from .models import Cars

def car_search_context(request):
    brands = Cars.objects.values_list('brand', flat=True).distinct()  # Get distinct brands
    transmissions = Cars.objects.values_list('transmission', flat=True).distinct()  # Get distinct transmissions
    cars = Cars.objects.all()  # Get all cars
    
    return {
        'brands': brands,
        'transmissions': transmissions,
        'cars': cars,  # Pass all cars to the context
    }
