from django.shortcuts import render

# Create your views here.


def shopping_home(request):
	print(request.GET.get('q'))
	keywords=request.GET.get('q')
	return render(request, 'shopping/home.html', {})
