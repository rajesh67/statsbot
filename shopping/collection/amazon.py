from urllib.parse import urlparse, parse_qs
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement

from django.conf import settings
from shopping.models import (
	Store,
	SearchProduct,
	SearchProductImage,
)
import bottlenose
import json


class AmazonSearchAPIHandler():
	def __init__(self, *args, **kwargs):
		self.store=Store.objects.get(short_name="amazon")
		self.amazon_handle=bottlenose.Amazon(self.store.affiliate_id, self.store.affiliate_token, "statsbot.org-21", Region= 'IN')

	def get_search_results(self, keywords):
		resp=self.amazon_handle.ItemSearch(Keywords=keywords, SearchIndex='All', ResponseGroup='Medium')
		return resp

	def parse_products_from_xml(self, data):
		products=[]
		root=ElementTree.fromstring(data)
		data=root.findall('./')
		if len(data)==2:
			items=data[-1]
			childs=items.getchildren()
			# Request Tag Processing
			reqChilds=childs[0].getchildren()
			isValid=reqChilds[0].text
			print(isValid)
			if isValid:
				totalResults=int(childs[1].text)
				totalPages=int(childs[2].text)
				moreSearchResultURL=childs[3].text
				# Extract Amazon Items Data from the Response
				for itemData in childs[4:]:
					allData=itemData.findall('./')
					baseUrl='{http://webservices.amazon.com/AWSECommerceService/2013-08-01}'
					finalData={}
					for node in allData:
						tag=node.tag.replace(baseUrl,"").strip()
						if tag=="ASIN":
							finalData.update({'asin':node.text})
						elif tag=="DetailPageURL":
							finalData.update({'pageUrl': node.text})
						elif tag=='ItemLinks':
							urls=[]
							for itemLink in node.findall('./'):
								linkItems=itemLink.findall('./')
								desc=linkItems[0].text
								url=linkItems[1].text
								urls.append({desc:url})
							finalData.update({'productLinks' : urls})
						elif tag=='SmallImage':
							imageData=node.findall('./')
							url=''
							size='{width}:{height}'
							for dat in imageData:
								width=''
								height=''
								subTag=dat.tag.replace(baseUrl,"").strip()
								if subTag=='URL':
									url=dat.text
								elif subTag=='Height':
									height=dat.text
								elif subTag=='Width':
									width=dat.text
								size=size.format(width=width, height=height)
							finalData.update({'smallImage': {size:url}})
						elif tag=='MediumImage':
							imageData=node.findall('./')
							url=''
							size='{width}:{height}'
							for dat in imageData:
								width=''
								height=''
								subTag=dat.tag.replace(baseUrl,"").strip()
								if subTag=='URL':
									url=dat.text
								elif subTag=='Height':
									height=dat.text
								elif subTag=='Width':
									width=dat.text
								size=size.format(width=width, height=height)
							finalData.update({'mediumImage': {size:url}})
						elif tag=='LargeImage':
							imageData=node.findall('./')
							url=''
							size='{0}:{1}'
							for dat in imageData:
								width=''
								height=''
								subTag=dat.tag.replace(baseUrl,"").strip()
								if subTag=='URL':
									url=dat.text
								elif subTag=='Height':
									height=dat.text
								elif subTag=='Width':
									width=dat.text
							finalData.update({'largeImage': {size.format(width, height):url}})
						elif tag=='ImageSets':
							pass
						elif tag=='ItemAttributes':
							attributes=node.getchildren()
							for attr in attributes:
								tag=attr.tag.replace(baseUrl, "").strip()
								if tag=='Manufacturer':
									finalData.update({'Brand': attr.text})
								elif tag=='Title':
									finalData.update({'Title': attr.text})
								elif tag=='ProductGroup':
									finalData.update({'ProductGroup': attr.text})
						elif tag=='OfferSummary':
							offers=[]
							for child in node.getchildren():
								tag=child.tag.replace(baseUrl,"").strip()
								if tag=='LowestNewPrice':
									for priceChild in child.getchildren():
										offer={}
										newTag=priceChild.tag.replace(baseUrl,"").strip()
										if newTag=='Amount':
											amount=int(priceChild.text)/100
											offer.update({'amount':amount})
										elif newTag=='CurrencyCode':
											currency=priceChild.text
											offer.update({'currency':currency})
										elif newTag=='FormattedPrice':
											offer.update({'sellingPrice':priceChild.text})
										offers.append(offer)
							finalData.update({'offers':offers})
						elif tag=='EditorialReviews':
							reviews=[]
							for review in node.getchildren():
								source=''
								content=''
								for child in review.getchildren():
									tag=child.tag.replace(baseUrl, "").strip()
									if tag=='Source':
										source=child.text
									elif tag=='Content':
										content=child.text
								reviews.append({'source':source, 'content':content})
							finalData.update({'reviews':reviews})
					products.append(finalData)
				return products	
			else:
				print("Request Valid is not True")
		else:
			print("Response Doesn't Contains Any Items")