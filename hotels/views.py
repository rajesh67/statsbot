from django.shortcuts import render
from django.views.generic.base import View, TemplateView
# Create your views here.
from hotels.models import (
	Store
)

class HotelsHomeView(TemplateView):

	template_name="hotels/home.html"

	def get_context_data(self, **kwargs):
		context=super(HotelsHomeView, self).get_context_data(**kwargs)
		context['storesList']=Store.objects.all()
		return context
