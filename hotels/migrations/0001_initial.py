# Generated by Django 2.0 on 2018-03-25 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(blank=True, max_length=50, null=True)),
                ('home_url', models.URLField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('affiliate_id', models.CharField(max_length=100)),
                ('affiliate_token', models.CharField(max_length=250)),
                ('logo_image', models.ImageField(null=True, upload_to='stores/')),
            ],
        ),
    ]
