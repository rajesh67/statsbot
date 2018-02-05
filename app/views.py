from django.shortcuts import render, render_to_response

# Create your views here.
from shopping.models import Product

def home(request):
	return render(request, 'shopping/home.html', {'products':Product.objects.all()})