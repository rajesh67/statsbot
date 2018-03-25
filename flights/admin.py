from django.contrib import admin

# Register your models here.
from flights.models import Store, Category


admin.site.register(Store)
admin.site.register(Category)