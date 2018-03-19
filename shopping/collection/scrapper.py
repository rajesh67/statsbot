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
)
import datetime
import timestring
import xml.etree.ElementTree as ET

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

	def save_category_feeds(self, category_name):
		apiListings=self.get_apiListings()
		category_vars=apiListings[category_name]
		base_url=category_vars['availableVariants']['v1.1.0']['get']
		nextUrl=base_url
		while nextUrl:
			resp=requests.get(nextUrl, headers=self.params)
			data=json.loads(resp.content)
			nextUrl=data['nextUrl']
			products=[]
			imageUrls={}
			prices={}
			offers={}
			for product in data['productInfoList']:
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
			for product in saved_products:
				# Create Images for the Product
				images=[]
				pro.save()
				for size, url in imageUrls[product.productId]['imageUrls'].items():
					image=ProductImage(size=size, url=url, product=product)
					images.append(image)
				# Bulk Create Image instances
				saved_images=Image.objects.bulk_create(images)
				for image in saved_images:
					image.save() 
				# Update Price History for the Products
				retailPrice=prices[product.productId]['retailPrice']['amount']
				sellingPrice=prices[product.productId]['sellingPrice']['amount']
				specialPrice=prices[product.productId]['specialPrice']['amount']
				price=PriceHistory.objects.create(retailPrice=retailPrice, sellingPrice=sellingPrice, specialPrice=specialPrice, status=0, date=datetime.datetime.now(), product=product)
				# Updates Offers for the product
				for offer in offers[product.productId]['offers']:
					off, created=ProductOffer.objects.get_or_create(text=offer)
					off.products.add(product)
					off.save()
				# Finally Save the Product
				product.save()
		print("Category Feeds Saved Succefully")

	def update_category_feeds_prices(self, category_name):
		apiListings=self.get_apiListings()
		category_vars=apiListings[category_name]
		base_url=category_vars['availableVariants']['v1.1.0']['get']
		nextUrl=base_url
		while nextUrl:
			resp=requests.get(nextUrl, headers=self.params)
			data=json.loads(resp.content)
			nextUrl=data['nextUrl']
			prices=[]
			for product in data['productInfoList']:
				baseInfo=product['productBaseInfoV1']
				productId=baseInfo['productId']
				try:
					pro=Product.objects.filter(productId=productId).first()
					#Update Prices
					last_price_history=pro.pricehistory_set.last()
					new_price=baseInfo['flipkartSpecialPrice']['amount']
					price_history=PriceHistory.objects.create(
						retailPrice=baseInfo['maximumRetailPrice']['amount'],
						sellingPrice=baseInfo['flipkartSellingPrice']['amount'],
						specialPrice=baseInfo['flipkartSpecialPrice']['amount'],
						date=datetime.datetime.now(),
						status=0,
						product=pro,)
					# Update Offers
					offers=baseInfo['offers']
					pro.save()
				except Product.DoesNotExist:
					# Create the Product and save into database
					pro=Product.objects.create(productId=productId,
						productUrl=baseInfo['productUrl'],
						title=baseInfo['title'],
						brand=baseInfo['productBrand'],
						inStock=True if baseInfo['inStock']==1 else False,
						codAvailable=True if baseInfo['codAvailable']==1 else False,
						discountPercentage=baseInfo['discountPercentage'])
					# Save Product IMages
					images=[]
					for size, url in baseInfo['imageUrls']:
						image=Image(size=size, url=url, product=pro)
						images.append(image)
					saved_images=Image.objects.bulk_create(images)
					# Save or Update Prices
					price_history=PriceHistory.objects.create(sellingPrice=baseInfo['flipkartSellingPrice']['amount'],
						specialPrice=baseInfo['flipkartSpecialPrice']['amount'],
						retailPrice=baseInfo['maximumRetailPrice']['amount'],
						date=datetime.datetime.now(),
						status=0,
						product=pro)
					pro.save()
					# Update Offers
					for offer in baseInfo['offers']:
						offers=ProductOffer.objects.filter(text=offer)
						if offers:
							off=offers.first()
							off.products.add(pro)
							off.save()
							pro.save()
						else:
							# Create The offer
							off=Offer.objects.create(text=offer)
							off.products.add(pro)
							pro.save()
							off.save()
					pro.save()

class AmazonAPIHandler():

	def register(self):
		pass


class FlipkartAPIAdmin():
	def __init__(self,*args,**kwargs):
		self.headers={'Fk-Affiliate-Id':settings.FLIPKART_AFF_ID,'Fk-Affiliate-Token':settings.FLIPKART_AFF_TOKEN}
		return super(FlipkartAPIAdmin, self).__init__(*args, **kwargs)

	def save_offers_xml_data(self, type="json"):
		offers=[]
		resp=requests.get(settings.FLIPKART_OFFERS_XML_URL, headers=self.headers)
		if resp.ok:
			root=ET.fromstring(resp.content)
			#Find The List of All Available Offers
			allOffersList=root.findall('allOffersList')
			for off in allOffersList:
				availability=''
				category=''
				description=''
				endTime=''
				startTime=''
				imageUrls=[]
				title=''
				offer_url=''
				for offer in off.getchildren():
					# Find the Available Information for Individual Offers
					# 'LIVE', 'EXPIRED', 'COMING SOON'
					if offer.tag=='availability':
						availability=offer.text
					elif offer.tag=='category':
						category=offer.text
					elif offer.tag=='description':
						description=offer.text
					elif offer.tag=='endTime':
						endTime=offer.text
					elif offer.tag=='imageUrls':
						resolutionType=''
						image_url=''
						for child in offer.getchildren():
							if child.tag=='resolutionType':
								resolutionType=child.text
							elif child.tag=='url':
								image_url=child.text
						imageUrls.append({'resolutionType': resolutionType, 'url': image_url})
					elif offer.tag=='startTime':
						startTime=offer.text
					elif offer.tag=='title':
						title=offer.text
					elif offer.tag=='url':
						offer_url=offer.text
					# Create New Product Then Add the Images
					try:
						new_offer, created=Offer.objects.get_or_create(
							title=title,
							category=category,
							description=description,
							endTime=timestring.Date(endTime),
							startTime=timestring.Date(startTime),
							url=offer_url,
							availability=availability,
						)
						new_offer.save()
						# Create Images If there are any
						if created:
							if imageUrls:
								for imageUrl in imageUrls:
									resolutionType=imageUrl['resolutionType']
									image_url=imageUrl['url']
									image=OfferImage.objects.create(resolutionType=resolutionType.text, url=image_url.text, offer=new_offer)
							new_offer.save()
					except Exception as e:
						pass
		#Connection Problem
		print("Compelete!")

	def get_dotd_xml_data(self, type="json"):
		pass

	def get_individual_product_data(self, type="json"):
		pass

	def get_all_category_base_urls(self):
		pass

	def get_individual_category_feeds(self, category_name):
		pass

	def get_individual_category_delta_feeds(self, category_name):
		pass

	def save_feeds_data(self, products_json):
		pass


class FKOffersAPIHandler():
	def __init__(self,*args,**kwargs):
		self.headers={'Fk-Affiliate-Id':settings.FLIPKART_AFF_ID,'Fk-Affiliate-Token':settings.FLIPKART_AFF_TOKEN}
		self.store=Store.objects.get(short_name="flipkart")
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