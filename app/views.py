from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from graphos.sources.model import ModelDataSource
from graphos.renderers import flot
# Create your views here.
from shopping.models import Product, PriceHistory

def home(request):
	return HttpResponseRedirect('/shopping/')