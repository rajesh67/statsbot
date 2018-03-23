from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
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

def shopping_home(request):
	return render(request, 'shopping/home.html', {'dotdList':DOTD.objects.all()[:10], 'offersList': Offer.objects.all()[:10]})

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
	deals=DOTD.objects.all()
	return render(request, "shopping/deals.html", {'dealsList': deals,})

class OfferListView(ListView):
	model = Offer
	template_name="shopping/offers.html"
	context_object_name='offers'
	paginate_by=12
	queryset=Offer.objects.all()

class DOTDListView(ListView):
	model = DOTD
	template_name = "shopping/deals.html"
	context_object_name = "deals"
	paginate_by = 12
	queryset = DOTD.objects.all()

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
			searchHandle=FKSearchAPIHandler()
			productsList=searchHandle.get_search_results(keywords=keywords)
		return render(request, self.template_name, {'products': productsList})

class StoreDetailView(DetailView):
	model = Store
	template_name="shopping/store.html"
	context_object_name='store'

	def get_object(self):
		return Store.objects.get(short_name=self.kwargs.get('storeName'))

	def get_context_data(self, **kwargs):
		context=super(StoreDetailView, self).get_context_data(**kwargs)
		store=self.get_object()
		context['products']=store.product_set.filter(inStock=True)[:50]
		return context

class AboutUSView(TemplateView):
	template_name="index.html"

	def get_context_data(self, **kwargs):
		context=super(AboutUSView, self).get_context_data(**kwargs)
		return context

class WhyUSView(TemplateView):
	template_name="index.html"

	def get_context_data(self, **kwargs):
		context=super(WhyUSView, self).get_context_data(**kwargs)
		return context