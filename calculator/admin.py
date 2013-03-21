from django.contrib import admin
from calculator.models import City

class CityAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Geographic Coordinates', {'fields': ['lat', 'lng']}),
        ('Calculated Road Efficiency', {'fields': ['eff']}),
    ]

admin.site.register(City, CityAdmin)
