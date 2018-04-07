from django.shortcuts import render
from django.views.generic.base import View, TemplateView
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
