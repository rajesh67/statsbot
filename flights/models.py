from django.db import models
from django.core.files import File
# Create your models here.
import datetime
import csv
import io
from django.db.models.signals import post_save
from django.dispatch import receiver

class Store(models.Model):
	name=models.CharField(max_length=100)
	short_name=models.CharField(max_length=50, null=True, blank=True)
	home_url=models.URLField(max_length=150)
	description=models.TextField(null=True, blank=True)
	
	affiliate_id=models.CharField(max_length=100)
	affiliate_token=models.CharField(max_length=250)
	
	logo_image=models.ImageField(upload_to='stores/', null=True)
	
	cuelink_name=models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		return self.cuelink_name or self.name

class Category(models.Model):
	name=models.CharField(max_length=30)
	stores=models.ManyToManyField('Store', null=True)

	def __str__(self):
		return self.name

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
	data_file=models.FileField(upload_to='data/cuelinks/offers/flights/')
	
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

