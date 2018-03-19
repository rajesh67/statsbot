from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from shopping.views import (shopping_home,
	DOTDListView,
	OfferListView,
	FeedsListView,
	CategoryListView,
	SearchResultsView,
)

urlpatterns=[
	url('^$', FeedsListView.as_view(), name="shopping-home"),
	url('^search$', SearchResultsView.as_view(), name="search-products"),
	url('^(?P<categoryName>[a-zA-Z]+)/$', CategoryListView.as_view(), name="category-products"),
	url('^p/offers/$', OfferListView.as_view(), name="shopping-offers"),
	url('^p/deals/$', DOTDListView.as_view(), name="shopping-deals"),
]