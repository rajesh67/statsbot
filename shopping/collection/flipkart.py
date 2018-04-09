import os
from django.conf import settings
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from shopping.models import (Product, 
	PriceHistory, 
	ProductOffer, 
	ProductImage,
	SearchProductImage,
	Offer, 
	OfferImage,
	DOTDImage,
	DOTD,
	Store,
	Category,
	SearchProduct,
	ProductPrice,
)
import datetime
import timestring
import xml.etree.ElementTree as ET
from multiprocessing import Process
from urllib.parse import urlparse, parse_qs
from itertools import islice
from django.db import transaction

def requests_retry_session(retries=3, backoff_factor=0.3,status_forcelist=('500','502', '504'), session=None):
	session=session or requests.Session()
	retry=Retry(
		total=retries,
		read=retries,
		connect=retries,
		backoff_factor=backoff_factor,
		status_forcelist=status_forcelist,
	)
	adapter=HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	return session


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
		offers=[]
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
			offers.append(new_offer)
		return offers
			
	def save_dotd_feeds(self, dotdList):
		deals=[]
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
			deals.append(new_dotd)
		return deals


class FKFeedAPIHandler():
	def __init__(self,category,*args,**kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.category, created=Category.objects.get_or_create(name=category)
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
		print(category_vars['availableVariants']['v1.1.0'].keys())
		self.category.deltaGetURL=category_vars['availableVariants']['v1.1.0']['deltaGet']
		# self.category.topFeedsURL=category_vars['availableVariants']['v1.1.0']['top']
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
			self.category.last_version=data['version']
			self.category.current_version=data['version']
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

	@transaction.atomic
	def update_delta_feeds(self, deltaFeeds):
		def get_product(baseInfo):
			return Product.objects.get(productId=baseInfo['productId'])

		# check For Offer Updates
		def update_offers(data):
			baseInfo=data['productBaseInfoV1']
			product=get_product(baseInfo)
			#

		# Update Prices
		def update_pricehistory(data):
			baseInfo=data['productBaseInfoV1']
			product=get_product(baseInfo)
			specialPrice=baseInfo['flipkartSpecialPrice']['amount']
			history=PriceHistory()
			lastPrice=product.pricehistory_set.last()
			if specialPrice!=lastPrice.specialPrice:
				history.date=datetime.datetime.now()
				history.retailPrice=baseInfo['maximumRetailPrice']['amount']
				history.sellingPrice=baseInfo['flipkartSellingPrice']['amount']
				history.specialPrice=baseInfo['flipkartSpecialPrice']['amount']
				history.product=product
				history.status="-1"
				history.save()
				# print("Price Changed For: %s"%(product.title))
				# print("Last Price : %d"%(lastPrice.specialPrice))
				# print("Current Price : %d, specialPrice : %d"%(lastPrice.specialPrice, specialPrice))
			
		# Update Stock Information
		def update_availability(data):
			baseInfo=data['productBaseInfoV1']
			currStock=True if baseInfo['inStock']==1 or baseInfo['inStock']=='yes' or baseInfo['inStock']==1 else False
			product=get_product(baseInfo)
			if currStock!=product.inStock:
				product.inStock=currStock
				product.save()

		for product in deltaFeeds['products']:
			#update prices
			update_availability(product)
			update_pricehistory(product)
			update_offers(product)
		print("Delta Feeds Updated Successfully")

	@transaction.atomic
	def update_all_delta_feeds(self):
		listings=self.get_base_urls()
		deltaGetURL=listings[self.category.name]['availableVariants']['v1.1.0']['deltaGet']
		data=urlparse(deltaGetURL)
		json_qs=parse_qs(data.query)
		resp=requests.get(deltaGetURL, headers=self.headers)
		if resp.status_code==200:
			data=json.loads(resp.content)
			catId=data['category']
			version=data['version']
			if version!=self.category.current_version:
				DELTA_URL=settings.FLIPKART_DELTA_FEEDS_JSON_URL.format(
					version=self.category.last_version, 
					catId=self.category.catId
					)
				# resp=requests.get(DELTA_URL, headers=self.headers, params=data.query)
				nextUrl=DELTA_URL
				while nextUrl:
					resp=requests.get(nextUrl, headers=self.headers)
					if resp.status_code==200:
						data=json.loads(resp.content)
						self.update_delta_feeds(data)
						nextUrl=data['nextUrl']
					else:
						break
				# Now Updates The Version Of the Category
				self.category.baseApiURL=listings[self.category.name]['availableVariants']['v1.1.0']['get']
				self.category.deltaGetURL=deltaGetURL
				self.category.topFeedsURL=listings[self.category.name]['availableVariants']['v1.1.0']['top']
				self.category.last_updated_on=datetime.datetime.now()
				self.category.last_version=self.category.current_version
				self.category.current_version=version
				self.category.save()
			else:
				print("Category Not Changed")
		else:
			print(resp, resp.url)

class FKSearchAPIHandler():
	def __init__(self, *args, **kwargs):
		self.store=Store.objects.get(short_name="flipkart")
		self.headers={'Fk-Affiliate-Id':self.store.affiliate_id,'Fk-Affiliate-Token':self.store.affiliate_token}
		return super(FKSearchAPIHandler, self).__init__(*args, **kwargs)

	@transaction.atomic
	def get_search_results(self, keywords):
		
		def create_bulk_products(self, objs):
			batch_size=100
			while True:
				batch=list(islice(objs, batch_size))
				if not batch:
					break
				SearchProduct.objects.bulk_create(batch, batch_size)

		def save_search_results(data):
			productsList=[]
			products=data['products']
			for product in list(products):
				baseInfo=product['productBaseInfoV1']
				productId=baseInfo['productId']
				new_prod, created=SearchProduct.objects.get_or_create(
					store=self.store,
					title=baseInfo['title'],
					productId=baseInfo['productId'],
					productUrl=baseInfo['productUrl'],
					brand=baseInfo['productBrand'],
					inStock=baseInfo['inStock'],
					codAvailable=baseInfo['codAvailable'],
				)
				if created:
					priceHistory=ProductPrice.objects.create(
						sellingPrice=baseInfo['flipkartSpecialPrice']['amount'],
						retailPrice=baseInfo['maximumRetailPrice']['amount'],
						updated_on=datetime.datetime.now(),
						product=new_prod,
						discountPercentage=baseInfo['discountPercentage'],
					)
					imageUrls=baseInfo['imageUrls']
					for size, url in imageUrls.items():
						image=SearchProductImage.objects.create(
							product=new_prod,
							size=size,
							url=url,
						)
				productsList.append(new_prod)
			return productsList

		resp=requests.get(settings.FLIPKART_SEARCH_URL, headers=self.headers, params={'query': keywords, 'resultCount':12})
		if resp.status_code==200:
			data=json.loads(resp.content)
			# Save These Products and return Back
			productsList=save_search_results(data)
			return productsList
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
					print(e)
		else:
			print(resp.status_code, resp.content)