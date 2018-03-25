from django.conf.urls import url, include

from busses.views import BusesHomeView

urlpatterns=[
	url(r'^$', BusesHomeView.as_view(), name="buses-home")
]