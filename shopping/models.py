from django.db import models
from urllib.parse import urlparse, parse_qs
# Create your models here.

class Store(models.Model):
	name=models.CharField(max_length=100)
	short_name=models.CharField(max_length=10, null=True, blank=True)
	home_url=models.URLField(max_length=150)
	description=models.TextField(null=True, blank=True)
	affiliate_id=models.CharField(max_length=100)
	affiliate_token=models.CharField(max_length=250)
	logo_image=models.ImageField(upload_to='stores/', null=True)

	def __str__(self):
		return self.name

class Category(models.Model):
	catId=models.CharField(max_length=30, null=True, blank=True)
	name=models.CharField(max_length=30)
	
	baseApiURL=models.URLField(max_length=2500, null=True, blank=True)
	deltaGetURL=models.URLField(max_length=2500, null=True, blank=True)
	topFeedsURL=models.URLField(max_length=2500, null=True, blank=True)

	store=models.ForeignKey('Store', on_delete=models.CASCADE)
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

	store=models.ForeignKey('Store', on_delete=models.CASCADE, related_name="search_products")

	def __str__(self):
		return self.title

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
	product=models.ForeignKey('Product', on_delete=models.CASCADE)

	def __str__(self):
		return self.status

class ProductOffer(models.Model):
	text=models.CharField(max_length=300)
	products=models.ManyToManyField(Product)

	def __str__(self):
		return self.text

class BaseImage(models.Model):
	size=models.CharField(max_length=20)
	url=models.URLField(max_length=500)

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
		return self.dotdimage_set.get(size='default')

class DOTDImage(BaseImage):
	dotd=models.ForeignKey('DOTD', on_delete=models.CASCADE)

	def __str__(self):
		return self.size