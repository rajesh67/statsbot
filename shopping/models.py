from django.db import models
from urllib.parse import urlparse, parse_qs
import datetime
# Create your models here.
import csv
import io
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from . import search

class Store(models.Model):
	name=models.CharField(max_length=100, null=True, blank=True)
	short_name=models.CharField(max_length=10, null=True, blank=True)
	home_url=models.URLField(max_length=150, null=True, blank=True)
	description=models.TextField(null=True, blank=True)
	affiliate_id=models.CharField(max_length=100, null=True, blank=True)
	affiliate_token=models.CharField(max_length=250, null=True, blank=True)
	logo_image=models.ImageField(upload_to='stores/', null=True)

	cuelink_name=models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		return self.cuelink_name

class Category(models.Model):
	catId=models.CharField(max_length=30, null=True, blank=True)
	name=models.CharField(max_length=30)
	
	baseApiURL=models.URLField(max_length=2500, null=True, blank=True)
	deltaGetURL=models.URLField(max_length=2500, null=True, blank=True)
	topFeedsURL=models.URLField(max_length=2500, null=True, blank=True)

	store=models.ManyToManyField('Store', related_name="categories")
	feedsListed=models.BooleanField(default=False)
	last_updated_on=models.DateTimeField(null=True, blank=True)

	last_version=models.PositiveIntegerField(default=0)
	current_version=models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.name

	def get_query_params(self):
		data=urlparse(self.baseApiURL)
		return data.query

class SearchProduct(models.Model):
	productId=models.CharField(max_length=30)
	title=models.CharField(max_length=500)
	productUrl=models.URLField(max_length=500)
	brand=models.CharField(max_length=50)
	inStock=models.BooleanField(default=False)
	codAvailable=models.BooleanField(default=False)
	topSeller=models.BooleanField(default=False)
	catName=models.CharField(max_length=100, null=True, blank=True)

	store=models.ForeignKey('Store', on_delete=models.CASCADE, related_name="search_products")

	def __str__(self):
		return self.title

	def indexing(self):
		image=self.get_default_image()
		price=self.prices.last()
		obj = search.ProductIndex(
			meta={'id': self.id},
			store_name=self.store.name,
			productId=self.productId,
			title=self.title,
			productUrl=self.productUrl,
			brand=self.brand,
			inStock=self.inStock,
			codAvailable=self.codAvailable,
			topSeller=self.topSeller,
			catName=self.catName,
			imageUrl=image.url if image else None,
			sellingPrice=price.sellingPrice if price else 0,
		)
		obj.save()
		return obj.to_dict(include_meta=True)

	def get_default_image(self):
		if self.store.short_name=='amazon':
			return self.searchproductimage_set.filter(size='large').first()
		else:
			return self.searchproductimage_set.filter(size='400x400').first()

class ProductDescription(models.Model):
	content=models.TextField()
	product=models.ForeignKey('SearchProduct', on_delete=models.CASCADE)

	def __str__(self):
		return self.content

class ProductLinks(models.Model):
	source=models.CharField(max_length=50, null=True, blank=True)
	link=models.URLField(max_length=2500)
	product=models.ForeignKey('SearchProduct', on_delete=models.CASCADE)

	def __str__(self):
		return self.source


class ProductPrice(models.Model):
	updated_on=models.DateTimeField(auto_now_add=True)
	retailPrice=models.FloatField(default=0)
	sellingPrice=models.FloatField(default=0)
	discountPercentage=models.FloatField(default=0)
	product=models.ForeignKey('SearchProduct', on_delete=models.CASCADE, null=True, related_name="prices")

	def __str__(self):
		return str(self.sellingPrice)

class Product(models.Model):
	productId=models.CharField(max_length=30)
	title=models.CharField(max_length=500)
	productUrl=models.URLField(max_length=500)
	brand=models.CharField(max_length=50)
	inStock=models.BooleanField(default=False)
	codAvailable=models.BooleanField(default=False)
	discountPercentage=models.FloatField(default=0.0)
	topSeller=models.BooleanField(default=False)

	store=models.ForeignKey('Store', on_delete=models.CASCADE)
	category=models.ForeignKey('Category', on_delete=models.CASCADE, default=None, null=True, blank=True)


	def __str__(self):
		return self.title

	def get_default_image(self):
		return self.productimage_set.filter(size="400x400").first()

	def indexing(self):
		image=self.get_default_image()
		price=self.prices.last()
		obj = search.ProductIndex(
			meta={'id': self.id},
			store_name=self.store.name,
			productId=self.productId,
			title=self.title,
			productUrl=self.productUrl,
			brand=self.brand,
			inStock=self.inStock,
			codAvailable=self.codAvailable,
			topSeller=self.topSeller,
			catName=self.category.name,
			imageUrl=image.url if image else None,
			sellingPrice=price.sellingPrice if price else 0,
		)
		obj.save()
		return obj.to_dict(include_meta=True)

class PriceHistory(models.Model):
	PRICE_STATUS=(
		('-1','decreased'),
		('0','fixed'),
		('1', 'increased')
	)
	date=models.DateTimeField()
	retailPrice=models.FloatField(default=0)
	sellingPrice=models.FloatField(default=0)
	specialPrice=models.FloatField(default=0)
	status=models.CharField(max_length=10, choices=PRICE_STATUS,default='0')
	product=models.ForeignKey('Product', on_delete=models.CASCADE, related_name="prices")

	def __str__(self):
		return self.status

class ProductOffer(models.Model):
	text=models.CharField(max_length=300)
	products=models.ManyToManyField(Product)

	def __str__(self):
		return self.text

class BaseImage(models.Model):
	size=models.CharField(max_length=20)
	url=models.URLField(max_length=2500)

	class Meta:
		abstract = True

class SearchProductImage(BaseImage):
	product=models.ForeignKey('SearchProduct', on_delete=models.CASCADE)

	def __str__(self):
		return self.size

class ProductImage(BaseImage):
	product=models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.size


class Offer(models.Model):
	availability=models.CharField(max_length=10, null=True, blank=True)
	category=models.CharField(max_length=30, null=True, blank=True)
	description=models.CharField(max_length=256, null=True, blank=True)
	endTime=models.DateTimeField()
	startTime=models.DateTimeField()
	title=models.CharField(max_length=250)
	url=models.TextField()
	created_on=models.DateTimeField()
	store=models.ForeignKey('Store', on_delete=models.CASCADE)

	def __str__(self):
		return self.title

	def get_default_image(self):
		return self.offerimage_set.get(size='mid')

	def is_live(self):
		if self.endTime.date().ctime()<datetime.datetime.now().ctime():
			self.availability='EXPIRED'
			self.save()
			return False
		return True

class OfferImage(BaseImage):
	offer=models.ForeignKey('Offer', on_delete=models.CASCADE)

	def __str__(self):
		return self.size

class DOTD(models.Model):
	title=models.CharField(max_length=250)
	description=models.CharField(max_length=256, null=True, blank=True)
	url=models.URLField(max_length=500)
	availability=models.CharField(max_length=10, null=True, blank=True)
	created_on=models.DateTimeField()
	store=models.ForeignKey('Store', on_delete=models.CASCADE)

	def __str__(self):
		return self.title

	def get_default_image(self):
		return self.dotdimage_set.get(size='high')

class DOTDUpdate(models.Model):
	created_on=models.DateTimeField(default=datetime.datetime.now())

	def __str__(self):
		return created_on

class DOTDImage(BaseImage):
	dotd=models.ForeignKey('DOTD', on_delete=models.CASCADE)

	def __str__(self):
		return self.size

class CuelinkOffer(models.Model):
	offerId=models.CharField(max_length=10)
	title=models.CharField(max_length=1024)
	categories=models.CharField(max_length=256, blank=True, null=True)
	description=models.TextField(blank=True, null=True)
	terms=models.TextField(blank=True, null=True)
	coupoun_code=models.CharField(max_length=50, null=True, blank=True)
	url=models.URLField(max_length=2500)
	status=models.CharField(max_length=10)
	startTime=models.DateTimeField(null=True)
	endTime=models.DateTimeField(null=True)
	imageUrl=models.URLField(max_length=2500)

	store=models.ForeignKey('Store', related_name="cuelink_offers", on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.title


class OfferUpdate(models.Model):
	created_on=models.DateTimeField(default=datetime.datetime.now())
	data_file=models.FileField(upload_to='data/cuelinks/offers/shopping/')
	
	def __str__(self):
		return self.created_on.date().ctime()

	def save_offers(self):
		data=self.data_file.open('r')
		lines=data.read().split('\n')
		for line in lines[1:]:
			off=csv.DictReader(io.StringIO(line))
			offer=off.fieldnames
			if offer:
				off, created=CuelinkOffer.objects.get_or_create(
					offerId=int(offer[0]), 
					startTime=datetime.datetime.strptime(offer[9], '%Y-%m-%d'),
					endTime=datetime.datetime.strptime(offer[10], '%Y-%m-%d')
				)
				if created:
					off.title=offer[1]
					off.categories=offer[3]
					off.description=offer[4]
					off.terms=offer[5]
					off.coupoun_code=offer[6]
					off.url=offer[7]
					off.status=offer[8]
					off.imageUrl=offer[12]
					off.store, created=Store.objects.get_or_create(cuelink_name=offer[2])
					off.save()
				else:
					# Update if the offer has been expired
					if off.endTime.ctime()<datetime.datetime.now().ctime():
						off.status='expired'
						off.save()

@receiver(post_save, sender=OfferUpdate)
def save_profile(sender, instance, **kwargs):
    instance.save_offers()

# @receiver(post_save, sender=SearchProduct)
# def index_post(sender, instance, **kwargs):
#     instance.indexing()