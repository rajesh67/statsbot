# Generated by Django 2.0 on 2018-04-11 18:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_auto_20180411_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='image',
            field=models.FileField(upload_to='campaigns/'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='posted_on',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 11, 23, 57, 17, 292164)),
        ),
    ]
