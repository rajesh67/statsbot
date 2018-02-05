import os
from django.conf import settings
import requests
import json
from shopping.models import Product

class FlipkartAPIHandler():
	
	def __init__(self):
		self.params={'Fk-Affiliate-Id':settings.FLIPKART_AFF_ID, 'Fk-Affiliate-Token': settings.FLIPKART_AFF_TOKEN}
	
	def get_apiListings(self):
		resp=requests.get(settings.FLIPKART_BASE_URL, headers=self.params)
		json_data=json.loads(resp.content)
		apiListings=json_data['apiGroups']['affiliate']['apiListings']
		print("Query Done")
		return apiListings

	def get_category_products(self, category_name):
		apiListings=self.get_apiListings()
		category_vars=apiListings[category_name]
		base_url=category_vars['availableVariants']['v1.1.0']['get']
		resp=requests.get(base_url, headers=self.params)
		json_data=json.loads(resp.content)
		productsList=json_data['productInfoList']
		nextUrl=json_data['nextUrl']
		print("Query Done")
		return (productsList, nextUrl)

	def get_specific_url_products(self, base_url):
		resp=requests.get(base_url, headers=self.params)
		json_data=json.loads(resp.content)
		productsList=json_data['productInfoList']
		nextUrl=json_data['nextUrl']
		print("Query Done")
		return (productsList, nextUrl)

	def save_in_db(self, category_name):
		initial_resp=self.get_category_products(category_name)
		nextUrl=initial_resp[1]
		products=initial_resp[0]
		for p in products:
			product, created=Product.objects.get_or_create(title=p['productBaseInfoV1']['title'])

		while nextUrl:
			resp=self.get_specific_url_products(nextUrl)
			products=resp[0]
			for p in products:
				baseInfo=p['productBaseInfoV1']
				product, created=Product.objects.get_or_create(title=baseInfo['title'])
				if created:
					product.productId=baseInfo['productId']
					product.productUrl=baseInfo['productUrl']
					product.save()
			nextUrl=resp[1]
		print("Saved In DB")

class SnapdealAPIHandler():
	pass