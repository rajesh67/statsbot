from django.contrib import admin

# Register your models here.
from hotels.models import (
	Store,
	OfferUpdate,
)

admin.site.register(Store)
admin.site.register(OfferUpdate)
