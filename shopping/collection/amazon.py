from urllib.parse import urlparse, parse_qs

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
		def parse_next_page_url(pageUrlElem):
			pass
		pass
