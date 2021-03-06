# Generated by Django 2.0 on 2018-04-06 01:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('busses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuelinkOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offerId', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=1024)),
                ('categories', models.CharField(blank=True, max_length=256, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('terms', models.TextField(blank=True, null=True)),
                ('coupoun_code', models.CharField(blank=True, max_length=50, null=True)),
                ('url', models.URLField(max_length=2500)),
                ('status', models.CharField(max_length=10)),
                ('startTime', models.DateTimeField(null=True)),
                ('endTime', models.DateTimeField(null=True)),
                ('imageUrl', models.URLField(max_length=2500)),
            ],
        ),
        migrations.CreateModel(
            name='OfferUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(default=datetime.datetime(2018, 4, 6, 6, 53, 48, 624914))),
                ('data_file', models.FileField(upload_to='data/cuelinks/offers/flights/')),
            ],
        ),
        migrations.AddField(
            model_name='store',
            name='cuelink_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='cuelinkoffer',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cuelink_offers', to='busses.Store'),
        ),
    ]
