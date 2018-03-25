from django.shortcuts import render
from django.views.generic.base import View, TemplateView
# Create your views here.
from busses.models import (
	Store
)

class BusesHomeView(TemplateView):

	template_name="buses/home.html"

	def get_context_data(self, **kwargs):
		context=super(BusesHomeView, self).get_context_data(**kwargs)
		context['storesList']=Store.objects.all()
		return context
