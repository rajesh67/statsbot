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
from shopping.collection.amazon import AmazonSearchAPIHandler, parse_products_from_xml, save_result_products
from shopping.models import (
	Product,
	PriceHistory, 
	ProductImage, 
	ProductOffer, 
	Offer,
	DOTD,
	Category,
	Store,
	CuelinkOffer,
)
import string
from django.core.paginator import InvalidPage, EmptyPage
import urllib
from . import search

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
		'stores':storesList,
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
	today=datetime.datetime.now().date()
	tomorrow=today+datetime.timedelta(1)
	today_start=datetime.datetime.combine(today, datetime.time())
	today_end=datetime.datetime.combine(tomorrow, datetime.time())
	deals=DOTD.objects.filter(created_on__lte=today_end, created_on__gte=today_start)
	return render(request, "shopping/deals.html", {'dealsList': deals,})

class OfferListView(ListView):
	model = Offer
	template_name="shopping/offers.html"
	context_object_name='offers'
	paginate_by=12
	queryset=Offer.objects.all()

	def get_queryset(self):
		queryset=super(OfferListView, self).get_queryset()
		today=datetime.datetime.now().date()
		tomorrow=today+datetime.timedelta(1)
		today_start=datetime.datetime.combine(today, datetime.time())
		today_end=datetime.datetime.combine(tomorrow, datetime.time())
		offers=queryset.filter(availability='LIVE')
		liveOffers=[]
		for offer in offers:
			if offer.is_live():
				liveOffers.append(offer)
		if self.kwargs.get('expired'):
			return queryset
		return liveOffers

	def get_context_data(self, **kwargs):
		context=super(OfferListView, self).get_context_data(**kwargs)
		context['stores']=Store.objects.all()
		return context

class DOTDListView(ListView):
	model = DOTD
	template_name = "shopping/deals.html"
	context_object_name = "deals"
	paginate_by = 12

	def get_queryset(self):
		queryset=super(DOTDListView, self).get_queryset()
		today=datetime.datetime.now().date()
		tomorrow=today+datetime.timedelta(1)
		today_start=datetime.datetime.combine(today, datetime.time())
		today_end=datetime.datetime.combine(tomorrow, datetime.time())
		return queryset.filter(created_on__lte=today_end, created_on__gte=today_start)

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
	paginate_by=20

	def get_queryset(self):
		# cat=Category.objects.get(name=self.kwargs.get('categoryName'))
		queryset=Product.objects.filter(category__name=self.kwargs.get('categoryName'))
		brandName=self.request.GET.get('brand', None)
		storeName=self.request.GET.get('store', None)
		if brandName and storeName:
			queryset=queryset.filter(brand=brandName, store__name=storeName)
		elif brandName:
			queryset=queryset.filter(brand=brandName)
		elif storeName:
			queryset=queryset.filter(store__name=storeName)
		return queryset

	def get(self, request, *args, **kwargs):
		if self.request.GET:
			url=self.request.GET.get('url')
			if not url:
				return super(CategoryListView, self).get(request, *args, **kwargs)
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
		return super(CategoryListView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context=super(CategoryListView, self).get_context_data(**kwargs)
		context['category']=Category.objects.get(name=self.kwargs.get('categoryName'))
		context['stores']=Store.objects.all()
		context['brands']=Product.objects.values('brand').distinct()
		context['total']=Product.objects.filter(category__name=self.kwargs.get('categoryName')).count()
		return context

class CategoryDetailView(DetailView):
	model = Category
	template_name="shopping/products.html"
	context_object_name='products'
	paginate_by=12

	def get_queryset(self):
		# cat=Category.objects.get(name=self.kwargs.get('categoryName'))
		return Category.objects.filter(name=self.kwargs.get('categoryName'))

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
		return super(CategoryDetailView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context=super(CategoryDetailView, self).get_context_data(**kwargs)
		context['category']=Category.objects.get(name=self.kwargs.get('categoryName'))
		context['store']=Store.objects.get(short_name=self.kwargs.get('storeName'))
		return context

class SearchResultsView(View):

	template_name = "shopping/search_results.html"

	def get(self, request, *args, **kwargs):
		keywords=request.GET.get('keywords')
		if keywords:
			print(keywords)
			output_data={}
			search_results_products=[]
			try:
				fkSearchHandle=FKSearchAPIHandler()
				productsList=fkSearchHandle.get_search_results(keywords=keywords)
				search_results_products.append({Store.objects.get(short_name='flipkart'):productsList})
			except Exception as e:
				search_results_products.append({Store.objects.get(short_name='flipkart'):[]})

			try:
				import time
				time.sleep(2)
				handle=AmazonSearchAPIHandler()
				# print("Could not make connection")
				results=handle.get_search_results(keywords=keywords)
				# print("Results Fetched")
				products=parse_products_from_xml(results)
				# print("Results Parsed")
				amazonProductsList=save_result_products(handle.store, products)
				# print("Results Saved")
				search_results_products.append({Store.objects.get(short_name='amazon'):amazonProductsList})
			except Exception as e:
				search_results_products.append({Store.objects.get(short_name='amazon'):[]})
				# print("Error While Fetching Amazon Products")
			# found_products=search.search(keywords)
			return render(request, self.template_name, {'data':search_results_products, 'stores':Store.objects.all()})
		return super(SearchResultsView, self).get(request, *args, **kwargs)

class StoreListView(ListView):
	model=Store
	template_name='shopping/store_list.html'
	context_object_name='stores'
	queryset=Store.objects.all()
	paginate_by=10

	def get_context_data(self, *args, **kwargs):
		context=super(StoreListView, self).get_context_data(*args, **kwargs)
		# context['stores']=Store.objects.all()
		return context

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
		offers=CuelinkOffer.objects.filter(store=self.get_object())
		catName=self.request.GET.get('category', None)
		if catName:
			offers=offers.filter(categories=catName)
		context['offers']=offers
		context['stores']=Store.objects.all()
		context['categories']=CuelinkOffer.objects.values('categories').distinct()
		return context

class AllOfferListView(ListView):
	model = CuelinkOffer
	template_name = "shopping/deals.html"
	context_object_name = "offers"
	paginate_by = 12
	queryset=CuelinkOffer.objects.all()

	def get_queryset(self):
		queryset=CuelinkOffer.objects.all()
		catName=self.request.GET.get('category', None)
		storeName=self.request.GET.get('store', None)
		if catName and storeName:
			queryset=queryset.filter(categories=catName, store__name=storeName)
		elif catName:
			queryset=queryset.filter(categories=catName)
		elif storeName:
			queryset=queryset.filter(store__name=storeName)
		return queryset

	def get_context_data(self, **kwargs):
		context=super(AllOfferListView, self).get_context_data(**kwargs)
		context['stores']=Store.objects.all()
		context['categories']=CuelinkOffer.objects.values('categories').distinct()
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
		context['stores']=Store.objects.all()
		return context