from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from shopping.views import (shopping_home,
	DOTDListView,
	OfferListView,
	FeedsListView,
	CategoryListView,
	SearchResultsView,
	StoreDetailView
)



urlpatterns=[
	url('^$', shopping_home, name="shopping-home"),
	url('^f/search/$', SearchResultsView.as_view(), name="search-products"),
	url('^h/(?P<storeName>[a-zA-Z0-9-_]+)/$', StoreDetailView.as_view(), name="store-homepage"),
	url('^h/(?P<storeName>[a-zA-Z0-9-_]+)/l/(?P<categoryName>[a-zA-Z0-9]+)/$', CategoryListView.as_view(), name="store-category"),
	# url('^h/(?P<storeName>[a-zA-Z0-9]+)/l/(?P<categoryName>[a-zA-Z0-9]+)/(?P<productId>[a-zA-Z0-9]+)/$', CategoryListView.as_view(), name="store-category"),
	url('^(?P<categoryName>[a-zA-Z-_]+)/$', CategoryListView.as_view(), name="category-products"),
	url('^p/offers/$', OfferListView.as_view(), name="shopping-offers"),
	url('^p/deals/$', DOTDListView.as_view(), name="shopping-deals"),
]