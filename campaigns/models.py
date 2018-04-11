from django.db import models

# Create your models here.
import datetime

class Category(models.Model):
	name=models.CharField(max_length=128)

	def __str__(self):
		return self.name

class Organization(models.Model):
	name=models.CharField(max_length=128)
	logo_image=models.ImageField(upload_to='organizations/', null=True)
	url=models.URLField(max_length=512, null=True)
	description=models.TextField()
	created_on=models.DateTimeField(default=datetime.datetime.now())
	email=models.EmailField()
	username=models.CharField(max_length=128)

	def __str__(self):
		return self.name

class Campaign(models.Model):
	title=models.CharField(max_length=512)
	short_description=models.CharField(max_length=2048)
	description=models.TextField(null=True)
	posted_on=models.DateTimeField(default=datetime.datetime.now())
	categories=models.ManyToManyField('Category', related_name='campaigns')
	image=models.ImageField(null=True)
	user_name=models.CharField(max_length=128, null=True)
	user_email=models.EmailField(null=True)

	organization=models.ForeignKey('Organization', null=True, related_name='campaigns', on_delete=models.CASCADE)

	def __str__(self):
		return self.title