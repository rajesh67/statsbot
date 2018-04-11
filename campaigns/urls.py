from django.conf.urls import url, include
from campaigns.views import campaigns_home, CampaignDetailView


urlpatterns=[
	url(r'^$', campaigns_home, name="campaigns-home"),
	url(r'^(?P<Id>[0-9a-zA-Z]+)/$', CampaignDetailView.as_view(), name="campaign-detail"),
]