# Generated by Django 2.0 on 2018-04-06 00:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0003_auto_20180406_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerupdate',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 6, 6, 0, 35, 598999)),
        ),
    ]