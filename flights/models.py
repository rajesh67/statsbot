from django.db import models

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
	name=models.CharField(max_length=30)
	stores=models.ManyToManyField('Store', null=True)

	def __str__(self):
		return self.name