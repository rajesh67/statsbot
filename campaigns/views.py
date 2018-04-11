from django.shortcuts import render, render_to_response

# Create your views here.
from campaigns.models import (
	Campaign, 
	Category
)

def campaigns_home(request):
	campaigns=Campaign.objects.all()
	return render_to_response('campaigns/home.html', {'campaigns': campaigns})