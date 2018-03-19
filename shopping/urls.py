from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from shopping.views import (shopping_home, 
	shopping_mobiles,
	shopping_offers,
	shopping_deals,
)

urlpatterns=[
	url('^$', shopping_home, name="shopping-home"),
	url('^mobiles/$', shopping_mobiles, name="shopping-mobiles"),
	url('^offers/$', shopping_offers, name="shopping-offers"),
	url('^deals/$', shopping_deals, name="shopping-deals"),
]