from django.shortcuts import render, render_to_response

# Create your views here.


def home(request):
	return render(request, 'shopping/home.html', {})