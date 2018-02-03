import os
from django.conf import settings
from urllib import request

class APIRegistration():
	def __init__(self, store):
		self.store=store

	def register(self, base_url):
		if self.store=='FLIPKART':
			params={'Fk-Affiliate-Id':settings['FLIPKART_AFF_ID'], 'Fk-Affiliate-Token': settings['FLIPKART_AFF_TOKEN']}
			req=request.Request(settings['FLIPKART_BASE_URL'], data=params)
			resp=request.urlopen(req)
		print ("Register Complete")