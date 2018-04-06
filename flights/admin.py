from django.contrib import admin

# Register your models here.
from flights.models import Store, Category, OfferUpdate


admin.site.register(Store)
admin.site.register(Category)
admin.site.register(OfferUpdate)