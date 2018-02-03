from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from shopping.views import shopping_home

urlpatterns=[
	url('/$', shopping_home, name="shopping-home"),
]