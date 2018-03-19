from django.shortcuts import render, render_to_response
from django.template import Context
from multiprocessing import Process, Value, Array
import json
from django.conf import settings
import requests
import datetime
from django.http import HttpResponse
from graphos.sources.model import ModelDataSource
from graphos.renderers import flot
# Create your views here.
from shopping.collection.scrapper import FlipkartAPIHandler
from shopping.models import (Product, 
	PriceHistory, 
	ProductImage, 
	ProductOffer, 
	Offer,
	DOTD,
)

def flipkart_search(keywords, results):
	headers={'Fk-Affiliate-Id': settings.FLIPKART_AFF_ID, 'Fk-Affiliate-Token':settings.FLIPKART_AFF_TOKEN}
	results=requests.get(settings.FLIPKART_SEARCH_URL, headers=headers, params={'query':keywords,'resultCount':10})
	json_data=json.loads(results.content)
	productsList=json_data['productInfoList']
	products=[]
	offers={}
	imageUrls={}
	prices={}
	for product in productsList:
		baseInfo=product['productBaseInfoV1']
		pro=Product(productId=baseInfo['productId'], 
			productUrl=baseInfo['productUrl'],
			title=baseInfo['title'],
			brand=baseInfo['productBrand'],
			inStock=True if baseInfo['inStock']==1 else False,
			codAvailable=True if baseInfo['codAvailable']==1 else False,
			discountPercentage=baseInfo['discountPercentage'])
		products.append(pro)
		imageUrls.update({baseInfo['productId'] : {'imageUrls':baseInfo['imageUrls']}})
		prices.update({baseInfo['productId'] : {'retailPrice': baseInfo['maximumRetailPrice'], 'sellingPrice':baseInfo['flipkartSellingPrice'], 'specialPrice': baseInfo['flipkartSpecialPrice']}})
		offers.update({baseInfo['productId']:{'offers':baseInfo['offers']}})
	# Create bulk products in DB
	saved_products=Product.objects.bulk_create(products)
	results=saved_products
	return results

def shopping_home(request):
	products_data=[]
	prices_data=[['Date','Price']]
	for product in Product.objects.all():
		for price_history in product.pricehistory_set.all():
			prices_data.append([price_history.date.day, price_history.specialPrice])
		products_data.append((product.productId,prices_data))
	data_source=ModelDataSource(PriceHistory.objects.all(), fields=['date', 'specialPrice'])
	chart = flot.LineChart(data_source)
	return render(request, 'shopping/home.html', {'products':Product.objects.all(), 'chart':chart})

def shopping_mobiles(request):
	products=Product.objects.all()
	keywords=request.GET.get('q')
	if keywords:
		# Open 2 Processess For Each Associated Store
		results=[]
		results=flipkart_search(keywords, results)
		return render(request, 'shopping/home.html',{'products':results})
	return render(request,"shopping/products.html", {})

def shopping_offers(request):
	offers=Offer.objects.all()
	return render(request, "shopping/offers.html", {'offersList': offers,})

def shopping_deals(request):
	deals=DOTD.objects.all()
	return render(request, "shopping/deals.html", {'dealsList': deals,})