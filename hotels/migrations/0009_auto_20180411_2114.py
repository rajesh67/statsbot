# Generated by Django 2.0 on 2018-04-11 15:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0008_auto_20180411_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerupdate',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 11, 21, 14, 47, 138067)),
        ),
    ]
