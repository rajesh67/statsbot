from django.conf import settings
from django.conf.urls import url, include

from flights.views import (
	FlightsHomeView,
	StoreListView,
)

urlpatterns=[
	url(r'^$', FlightsHomeView.as_view(), name="travels-home"),
	url('^f/$', StoreListView.as_view(), name="travels-store-directory"),
]