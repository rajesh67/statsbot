from django.contrib import admin

# Register your models here.
from shopping.models import *

admin.site.register(Store)
admin.site.register(Category)
admin.site.register(SearchProductImage)