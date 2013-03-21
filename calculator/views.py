from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from calculator.models import City
from eff import compute_lots, get_city_bounds_and_center

def index(request):
    city_list = City.objects.all()
    context = {'city_list': city_list}
    return render(request, 'calculator/index.html', context)

def calculate(request):
    city_name = request.POST['city_name']
    gcbc = get_city_bounds_and_center(city_name)
    city_center, actual_name = gcbc[1], gcbc[2]   
    print "Entered name: " + city_name
    print "Resolved name: " + actual_name
    try:
        print "Database hit!"
        c = City.objects.filter(name=actual_name)[0]
    except:
        print "Database miss!"
        eff = compute_lots(actual_name, 5, 10) # Uses compute_lots to find efficiency.
        c = City(lat=city_center[0],
                 lng=city_center[1],
                 eff=eff,
                 name=actual_name)
        c.save() # Saves c to database.
    return render(request, 'calculator/calculate.html', {'city': c})
