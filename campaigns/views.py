from django.shortcuts import render, render_to_response
from django.views.generic.detail import DetailView
# Create your views here.
from campaigns.models import (
	Campaign, 
	Category
)

def campaigns_home(request):
	campaigns=Campaign.objects.all()
	return render_to_response('campaigns/home.html', {'campaigns': campaigns})

class CampaignDetailView(DetailView):
	model=Campaign
	template_name="campaigns/campaign_detail.html"
	context_object_name='campaign'

	def get_object(self):
		return Campaign.objects.get(pk=self.kwargs.get('Id'))