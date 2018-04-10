from django.db import models

# Create your models here.
import datetime

class Category(models.Model):
	name=models.CharField(max_length=128)

	def __str__(self):
		return self.name

class Campaign(models.Model):
	title=models.CharField(max_length=512)
	short_description=models.CharField(max_length=2048)
	description=models.TextField(null=True)
	posted_on=models.DateTimeField(default=datetime.datetime.now())
	categories=models.ManyToManyField('Category', related_name='campaigns')
	image=models.ImageField(upload_to='campaigns/')

	def __str__(self):
		return title


class Contact(models.Model):
	SUBJECT_CHOICES=(
		('General','General Enquiries'),
		('Listing','Get Listed on our website'),
		('Partnership','Partnerships'),
		('Media','Media'),
		('Others','Others'),
	)
	created_on=models.DateTimeField(default=datetime.datetime.now())
	subject=models.CharField(max_length=50, choices=SUBJECT_CHOICES)
	name=models.CharField(max_length=128)
	email=models.EmailField()
	message=models.TextField()

	def __str__(self):
		return self.name