import datetime
from haystack import indexes

from shopping.models import (
	Store,
	Product,
)


class StoreIndex(indexes.SearchIndex, indexes.Indexable):
	text=indexes.CharField(document=True, use_template=True)
	name=indexes.CharField(model_attr="name")
	short_name=indexes.CharField(model_attr="short_name")

	name_auto=indexes.EdgeNgramField(model_attr='name')
	short_name_auto=indexes.EdgeNgramField(model_attr='short_name')
	suggestions=indexes.FacetCharField()

	def get_model(self):
		return Store

	def index_queryset(self, using=None):
		'''Used when the entire index for model is updated.'''
		return self.get_model().objects.all()

	def prepare(self, obj):
		prepared_data=super(StoreIndex, self).prepare(obj)
		prepared_data['suggestions']=prepared_data['text']
		return prepared_data

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
	text=indexes.CharField(document=True, use_template=True)
	title=indexes.CharField(model_attr="title")

	title_auto=indexes.EdgeNgramField(model_attr='title')
	suggestions=indexes.FacetCharField()

	def get_model(self):
		return Product

	def index_queryset(self, using=None):
		'''Used when the entire index for model is updated.'''
		return self.get_model().objects.all()

	def prepare(self, obj):
		prepared_data=super(ProductIndex, self).prepare(obj)
		prepared_data['suggestions']=prepared_data['text']
		return prepared_data