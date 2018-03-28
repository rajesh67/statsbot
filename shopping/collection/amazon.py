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
		resp=self.amazon_handle.ItemSearch(Keywords=keywords, SearchIndex='All')
		return resp

	def parse_products_from_xml(self, data):
		root=ElementTree.fromstring(data)
		data=root.findall('./')
		if len(data)==2:
			items=data[-1]
			childs=items.getchildren()
			# Request Tag Processing
			reqChilds=childs[0].getchildren()
			isValid=reqChilds[0].text
			if isValid==True:
				totalResults=int(reqChilds[1].text)
				totalPages=int(reqChilds[2].text)
				moreSearchResultURL=reqChilds[3].text
				# Extract Amazon Items Data from the Response
			else:
				print("Request Valid is not True")
		else:
			print("Response Doesn't Contains Any Items")