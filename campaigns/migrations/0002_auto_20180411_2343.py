# Generated by Django 2.0 on 2018-04-11 18:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='posted_on',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 11, 23, 43, 53, 715893)),
        ),
    ]
