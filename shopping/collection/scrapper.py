import os
from django.conf import settings
import requests
import json
from shopping.models import (Product, 
	PriceHistory, 
	ProductOffer, ProductImage, 
	Offer, 
	OfferImage,
	DOTDImage,
	DOTD,
	Store,
	Category,
)
import datetime
import timestring
import xml.etree.ElementTree as ET
from multiprocessing import Process
from urllib.parse import urlparse, parse_qs

class FKOffersAPIHandler():
	def __init__(self,*args,**kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		return super(FKOffersAPIHandler, self).__init__(*args, **kwargs)

	def get_offers_feeds(self, type="json"):
		offersList=[]
		if type=="json":
			resp=requests.get(settings.FLIPKART_OFFERS_JSON_URL, headers=self.headers)
			if resp.status_code==200:
				json_data=json.loads(resp.content)
				offersList=json_data['allOffersList']
		else:
			resp=requests.get(settings.FLIPKART_OFFERS_XML_URL, headers=self.headers)
			if resp.status_code==200:
				json_data=json.loads(resp.content)
				offersList=json_data['allOffersList']
		return offersList

	def get_dotd_feeds(self, type="json"):
		dotdList=[]
		if type=="json":
			resp=requests.get(settings.FLIPKART_DOTD_JSON_URL, headers=self.headers)
			if resp.status_code==200:
				json_data=json.loads(resp.content)
				dotdList=json_data['dotdList']
		else:
			resp=requests.get(settings.FLIPKART_DOTD_JSON_URL, headers=self.headers)
			if resp.status_code==200:
				json_data=json.loads(resp.content)
				dotdList=json_data['dotdList']
		return dotdList

	def save_offers_feeds(self, offersList):
		for offer in offersList:
			new_offer=Offer(
				startTime=datetime.datetime.fromtimestamp(offer['startTime']/1000.0),
				endTime=datetime.datetime.fromtimestamp(offer['endTime']/1000.0),
				title=offer['title'],
				description=offer['description'],
				url=offer['url'],
				category=offer['category'],
				availability=offer['availability'],
				store=self.store,
				created_on=datetime.datetime.now(),
			)
			newOffer=new_offer.save()
			print(new_offer.id, new_offer.title)
			offerImages=offer['imageUrls']
			for image in offerImages:
				off_img=OfferImage.objects.create(size=image.get('resolutionType'), url=image.get('url'), offer=new_offer)
			print(new_offer.startTime.date, new_offer.endTime.date)
			
	def save_dotd_feeds(self, dotdList):
		for dotd in dotdList:
			new_dotd=DOTD(
				title=dotd['title'],
				url=dotd['url'],
				description=dotd['description'],
				availability=dotd['availability'],
				store=self.store,
				created_on=datetime.datetime.now(),
			)
			new_dotd.save()
			for image in dotd['imageUrls']:
				img=DOTDImage.objects.create(size=image['resolutionType'], url=image['url'], dotd=new_dotd)
			print(new_dotd.title)


class FKFeedAPIHandler():
	def __init__(self,category,*args,**kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.category, created=Category.objects.get_or_create(name=category, store=self.store)
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		self.nextUrl=''
		return super(FKFeedAPIHandler, self).__init__(*args, **kwargs)

	def get_base_urls(self):
		resp=requests.get(settings.FLIPKART_BASE_URL, headers=self.headers)
		json_data=json.loads(resp.content)
		apiListings=json_data['apiGroups']['affiliate']['apiListings']
		return apiListings

	def get_category_feed_url(self):
		# Find If the Category Exists
		apiListings=self.get_base_urls()
		category_vars=apiListings[self.category.name]
		base_url=category_vars['availableVariants']['v1.1.0']['get']
		self.category.baseApiURL=base_url
		self.category.deltaGetURL=category_vars['availableVariants']['v1.1.0']['deltaGet']
		self.category.topFeedsURL=category_vars['availableVariants']['v1.1.0']['top']
		self.category.save()
		return base_url

	def get_nexturl_feeds(self, nextUrl):
		resp=requests.get(nextUrl, headers=self.headers)
		if resp.status_code==200:
			data=json.loads(resp.content)
			return data

	def save_current_version(self):
		resp=requests.get(self.category.deltaGetURL, headers=self.headers)
		if resp.status_code==200:
			data=json.loads(resp.content)
			self.category.catId=data['category']
			self.category.version=data['version']
			self.category.feedsListed=True
			self.category.last_updated_on=datetime.datetime.now()
			self.category.save()

	def save_category_feeds(self, productsData):
		productsList=productsData['products']
		for product in productsList:
			baseInfo=product['productBaseInfoV1']
			new_prod=Product(
				productId=baseInfo['productId'],
				title=baseInfo['title'],
				productUrl=baseInfo['productUrl'],
				brand=baseInfo['productBrand'],
				inStock=True if baseInfo['inStock']=='true' else False,
				codAvailable=True if baseInfo['codAvailable']=='true' else False,
				discountPercentage=True if baseInfo['discountPercentage']=='true' else False,
				store=self.store,
				category=self.category,
			)
			new_prod.save()
			for key, value in baseInfo['imageUrls'].items():
				image=ProductImage.objects.create(size=key, url=value, product=new_prod)
			# Create Price History Record At The Current Time
			priceHist=PriceHistory.objects.create(
				date=datetime.datetime.now(),
				retailPrice=baseInfo['maximumRetailPrice']['amount'],
				sellingPrice=baseInfo['flipkartSellingPrice']['amount'],
				specialPrice=baseInfo['flipkartSpecialPrice']['amount'],
				product=new_prod
			)
			for offer in baseInfo['offers']:
				new_off=ProductOffer.objects.create(text=offer)
				new_off.products.add(new_prod)
				new_off.save()
		nextUrl=productsData['nextUrl']
		return nextUrl

	def save_full_feeds(self):
		nextUrl=self.get_category_feed_url()
		while nextUrl:
			data=self.get_nexturl_feeds(nextUrl)
			nextUrl=self.save_category_feeds(data)
		self.save_current_version()
		print("All Products Saved Successfully")

class FKDeltaFeedAPIHandler():
	def __init__(self, category, *args, **kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.category, created=Category.objects.get_or_create(name=category)
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		return super(FKDeltaFeedAPIHandler, self).__init__(*args, **kwargs)

	def get_base_urls(self):
		resp=requests.get(settings.FLIPKART_BASE_URL, headers=self.headers)
		json_data=json.loads(resp.content)
		apiListings=json_data['apiGroups']['affiliate']['apiListings']
		return apiListings

	def save_current_version(self):
		resp=requests.get(self.category.deltaGetURL, headers=self.headers)
		if resp.status_code==200:
			data=json.loads(resp.content)
			self.category.catId=data['category']
			self.category.version=data['version']
			self.category.last_updated_on=datetime.datetime.now()
			self.category.save()

	def get_delta_feeds(self):
		data=urlparse(self.category.deltaGetURL)
		json_qs=parse_qs(data.query)
		DELTA_URL=settings.FLIPKART_DELTA_FEEDS_JSON_URL.format(version=self.category.version, catId=self.category.catId)
		resp=requests.get(DELTA_URL, headers=self.headers, params=data.query)
		print(resp.url)
		print(resp)
		if resp.status_code==200:
			return json.loads(resp.content)


	def save_delta_feeds(self):
		pass

class FKSearchAPIHandler():
	def __init__(self, *args, **kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		return super(FKSearchAPIHandler, self).__init__(*args, **kwargs)

	def get_search_results(self, keywords):
		resp=requests.get(settings.FLIPKART_SEARCH_URL, headers=self.headers, params={'query': keywords, 'resultCount':10})
		if resp.status_code==200:
			data=json.loads(resp.content)
			return data
		else:
			print(resp.status_code, resp.content)

class FKTopFeedAPIHandler():
	def __init__(self, category, *args, **kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.category, created=Category.objects.get_or_create(name=category)
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		return super(FKTopFeedAPIHandler, self).__init__(*args, **kwargs)

	def get_top_feeds(self):
		resp=requests.get(self.category.topFeedsURL, headers=self.headers)
		if resp.status_code==200:
			data=json.loads(resp.content)
			for product in data['products']:
				prodId=product['productBaseInfoV1']['productId']
				try:
					prod=Product.objects.get(productId=prodId)
					prod.topSeller=True
					prod.save()
				except Exception as e:
					print(e.stackTrace())
		else:
			print(resp.status_code, resp.content)

class AmazonSearchAPIHandler():

	def register(self):
		pass