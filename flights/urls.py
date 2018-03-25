from django.conf import settings
from django.conf.urls import url, include

from flights.views import (
	FlightsHomeView,
)

urlpatterns=[
	url(r'^$', FlightsHomeView.as_view(), name="flights-home")
]