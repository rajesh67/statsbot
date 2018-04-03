from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context
from multiprocessing import Process, Value, Array
import json
from django.conf import settings
import requests
import datetime
from django.http import HttpResponse
from graphos.sources.model import ModelDataSource
from graphos.renderers import flot
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
# Create your views here.
from shopping.collection.flipkart import FKFeedAPIHandler, FKSearchAPIHandler
from shopping.collection.amazon import AmazonSearchAPIHandler
from shopping.models import (
	Product,
	PriceHistory, 
	ProductImage, 
	ProductOffer, 
	Offer,
	DOTD,
	Category,
	Store,
)
import urllib

def handler404(request):
	return render(request, 'error.html', {})

def handler500(request):
	return render(request, 'error.html', {})


def shopping_home(request):
	storesList=Store.objects.all()
	deals_data={}
	offers_data={}
	products_data={}
	output_data={}
	today=datetime.datetime.now().date()
	tomorrow=today+datetime.timedelta(1)
	today_start=datetime.datetime.combine(today, datetime.time())
	today_end=datetime.datetime.combine(tomorrow, datetime.time())
	for store in Store.objects.all():
		deals_data.update({store:store.dotd_set.filter(created_on__lte=today_end, created_on__gte=today_start)[:11]})
		offers_data.update({store:store.offer_set.filter(availability='LIVE')[:11]})
		products_data.update({store:store.search_products.all()[:11]})
	return render(request, 'shopping/home.html', {
		'storesList':storesList,
		'offers_data':offers_data,
		'deals_data' : deals_data,
		'products_data':products_data,
	})

def shopping_mobiles(request):
	products=Product.objects.all()
	keywords=request.GET.get('q')
	if keywords:
		# Open 2 Processess For Each Associated Store
		results=[]
		results=flipkart_search(keywords, results)
		return render(request, 'shopping/home.html',{'products':results})
	return render(request,"shopping/products.html", {})

def shopping_deals(request):
	deals=DOTD.objects.filter(created_on=datetime.datetime.now())
	return render(request, "shopping/deals.html", {'dealsList': deals,})

class OfferListView(ListView):
	model = Offer
	template_name="shopping/offers.html"
	context_object_name='offers'
	paginate_by=12
	queryset=Offer.objects.all()

	def get_queryset(self):
		queryset=super(OfferListView, self).get_queryset()
		offers=queryset.filter(availability='LIVE')
		if self.kwargs.get('expired'):
			return queryset
		return offers


class DOTDListView(ListView):
	model = DOTD
	template_name = "shopping/deals.html"
	context_object_name = "deals"
	paginate_by = 12

	def get_queryset(self):
		queryset=super(DOTDListView, self).get_queryset()
		return queryset.filter(availability='LIVE')

class FeedsListView(ListView):
	model = Product
	template_name="shopping/home.html"
	context_object_name='products'
	paginate_by=12
	queryset=Product.objects.all()


class CategoryListView(ListView):
	model = Product
	template_name="shopping/products.html"
	context_object_name='products'
	paginate_by=12

	def get_queryset(self):
		# cat=Category.objects.get(name=self.kwargs.get('categoryName'))
		return Product.objects.filter(category__name=self.kwargs.get('categoryName'), store__short_name=self.kwargs.get('storeName'))

	def get(self, request, *args, **kwargs):
		if self.request.GET:
			url=self.request.GET.get('url')
			if not url:
				return super(StoreDetailView, self).get(request, *args, **kwargs)
			else:
				base_url='https://linksredirect.com/?'
				data={
					'pub_id':'29755CL26816',
					'subid':'statsbot',
					'source':'linkkit',
					'url':url,
				}
				newUrl=base_url+urllib.parse.urlencode(data)
				return HttpResponseRedirect(newUrl)
		return super(StoreDetailView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context=super(CategoryListView, self).get_context_data(**kwargs)
		context['category']=Category.objects.get(name=self.kwargs.get('categoryName'))
		context['store']=Store.objects.get(short_name=self.kwargs.get('storeName'))
		return context

class SearchResultsView(View):

	template_name = "shopping/search_results.html"

	def get(self, request, *args, **kwargs):
		keywords=request.GET.get('q')
		print(self.kwargs, request.GET.get('q'))
		if keywords:
			output_data={}
			try:
				fkSearchHandle=FKSearchAPIHandler()
				productsList=fkSearchHandle.get_search_results(keywords=keywords)
				output_data.update({Store.objects.get(short_name='flipkart'):productsList})
			except Exception as e:
				output_data.update({Store.objects.get(short_name='flipkart'):[]})

			try:
				amazSearchHandle=AmazonSearchAPIHandler()
				results=amazSearchHandle.get_search_results(keywords=keywords)
				products=amazSearchHandle.parse_products_from_xml(results)
				amazonProductsList=amazSearchHandle.save_result_products(products)
				output_data.update({Store.objects.get(short_name='amazon'):amazonProductsList})
			except Exception as e:
				output_data.update({Store.objects.get(short_name='amazon'):[]})
		return render(request, self.template_name, {'data':output_data})

class StoreDetailView(DetailView):
	model = Store
	template_name="shopping/store.html"
	context_object_name='store'

	def get(self, request, *args, **kwargs):
		if self.request.GET:
			url=self.request.GET.get('url')
			if not url:
				return super(StoreDetailView, self).get(request, *args, **kwargs)
			else:
				base_url='https://linksredirect.com/?'
				data={
					'pub_id':'29755CL26816',
					'subid':'statsbot',
					'source':'linkkit',
					'url':url,
				}
				newUrl=base_url+urllib.parse.urlencode(data)
				return HttpResponseRedirect(newUrl)
		return super(StoreDetailView, self).get(request, *args, **kwargs)

	def get_object(self):
		return Store.objects.get(short_name=self.kwargs.get('storeName'))

	def get_context_data(self, **kwargs):
		context=super(StoreDetailView, self).get_context_data(**kwargs)
		store=self.get_object()
		context['store']=store
		if not store.product_set.all():
			context['products']=store.search_products.all()[:12]
		else:
			context['products']=store.product_set.all()[:12]
		return context

class AboutUSView(TemplateView):
	template_name="index.html"

	def get_context_data(self, **kwargs):
		context=super(AboutUSView, self).get_context_data(**kwargs)
		return context

class WhyUSView(TemplateView):
	template_name="how_it_works.html"

	def get_context_data(self, **kwargs):
		context=super(WhyUSView, self).get_context_data(**kwargs)
		return context