from elasticsearch_dsl.connections import connections

connections.create_connection()

from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Integer, Keyword, Search
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models

connections.create_connection()


def search(title):
    s = Search().filter('term', title=title)
    response = s.execute()
    return response


class ProductIndex(DocType):
    productId = Text()
    title = Text()
    productUrl = Text()
    brand = Text()
    inStock=Text()
    codAvailable=Text()
    topSeller=Text()
    catName=Text()
    imageUrl=Text()
    sellingPrice=Integer()
    store_name=Text()

    class Meta:
        index = 'searchproduct-index'


def bulk_indexing():
    ProductIndex.init()
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.SearchProduct.objects.all().iterator()))
    bulk(client=es, actions=(b.indexing() for b in models.Product.objects.all().iterator()))
