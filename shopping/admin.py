from django.contrib import admin

# Register your models here.
from shopping.models import *


admin.site.register(Store)
admin.site.register(Category)
admin.site.register(CuelinkOffer)
admin.site.register(SearchProductImage)
admin.site.register(DOTDImage)
admin.site.register(OfferImage)
admin.site.register(OfferUpdate)