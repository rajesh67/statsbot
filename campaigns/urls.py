from django.conf.urls import url, include
from campaigns.views import campaigns_home


urlpatterns=[
	url(r'^$', campaigns_home, name="campaigns-home"),
]