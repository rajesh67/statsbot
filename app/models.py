from django.db import models

# Create your models here.
import datetime


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