from django.db import models

# Create your models here.

class Product(models.Model):
	productId=models.CharField(max_length=30)
	title=models.CharField(max_length=500)
	productUrl=models.URLField(max_length=500)
	brand=models.CharField(max_length=50)
	inStock=models.BooleanField(default=False)
	codAvailable=models.BooleanField(default=False)
	discountPercentage=models.FloatField(default=0.0)

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
	product=models.ForeignKey(Product, on_delete=models.CASCADE)
	status=models.CharField(max_length=10, choices=PRICE_STATUS,default='0')

	def __str__(self):
		return self.status

class Offer(models.Model):
	text=models.CharField(max_length=300)
	products=models.ManyToManyField(Product)

	def __str__(self):
		return self.text

class ImageUrl(models.Model):
	size=models.CharField(max_length=20)
	url=models.URLField(max_length=500)
	product=models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.size