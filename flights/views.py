from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
# Create your views here.
from flights.models import (
	Store,
	Category
)
from shopping import models

class FlightsHomeView(TemplateView):

	template_name="flights/home.html"

	def get_context_data(self, **kwargs):
		context=super(FlightsHomeView, self).get_context_data(**kwargs)
		context['storesList']=Store.objects.all()
		context['offers_data']=[{store: store.cuelink_offers.all()} for store in Store.objects.all()]
		context['stores']=models.Store.objects.all()
		return context

class StoreListView(ListView):
	model=Store
	template_name='flights/store_list.html'
	context_object_name='stores'
	queryset=Store.objects.all()
	paginate_by=12

	def get_context_data(self, *args, **kwargs):
		context=super(StoreListView, self).get_context_data(*args, **kwargs)
		# context['stores']=Store.objects.all()
		return context