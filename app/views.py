from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from graphos.sources.model import ModelDataSource
from graphos.renderers import flot
# Create your views here.
from shopping.models import Product, PriceHistory, Store
from flights.models import Store as TravelStore
from .models import Contact
from shopping.models import Store as ShoppingStore
from django.views.generic.edit import CreateView
import urllib

def home(request):
	return render_to_response('home.html',{'stores': Store.objects.all()})


def selectCampaign(request):
	storeName=request.GET.get('store')
	store=TravelStore.objects.get(short_name=storeName)
	return render_to_response('redirect.html', {'store':store})

def redirectToStore(request):
	url=request.GET.get('url', None)
	campId=request.GET.get('campId', None)
	if url and campId:
		base_url='https://linksredirect.com/?'
		params={
			'pub_id':'29755CL26816',
			'subid':campId,
			'source':'linkkit',
			'url':url,
		}
		link=base_url+urllib.parse.urlencode(params)
		return HttpResponseRedirect(link)
	else:
		base_url='https://linksredirect.com/?'
		params={
			'pub_id':'29755CL26816',
			'source':'linkkit',
			'url':url,
		}
		link=base_url+urllib.parse.urlencode(params)
		return HttpResponseRedirect(link)

class ContactView(CreateView):
	model=Contact
	template_name="contact_us.html"
	fields=['subject', 'name', 'email', 'message']