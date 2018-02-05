from django.shortcuts import render, render_to_response
from django.template import Context
# Create your views here.
from shopping.collection.scrapper import FlipkartAPIHandler
from shopping.models import Product 

def shopping_home(request):
	#Find Flipkart Category Names
	keywords=request.GET.get('q')
	return render(request, 'shopping/home.html',{})

def shopping_mobiles(request):
	products=Product.objects.all()
	return render(request,"shopping/products.html", Context({'products':products}))