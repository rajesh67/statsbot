from django.db import models

# Create your models here.

class Store(models.Model):
	name=models.CharField(max_length=100)
	short_name=models.CharField(max_length=10, null=True, blank=True)
	home_url=models.URLField(max_length=150)
	affiliate_id=models.CharField(max_length=100)
	affiliate_token=models.CharField(max_length=250)

	def __str__(self):
		return self.name

class Product(models.Model):
	productId=models.CharField(max_length=30)
	title=models.CharField(max_length=500)
	productUrl=models.URLField(max_length=500)
	brand=models.CharField(max_length=50)
	inStock=models.BooleanField(default=False)
	codAvailable=models.BooleanField(default=False)
	discountPercentage=models.FloatField(default=0.0)
	store=models.ForeignKey('Store', on_delete=models.CASCADE)

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
	product=models.ForeignKey(Product, on_delete=models.CASCADE)

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