from django.conf.urls import url, include

from hotels.views import HotelsHomeView

urlpatterns=[
	url(r'^$', HotelsHomeView.as_view(), name="hotels-home")
]