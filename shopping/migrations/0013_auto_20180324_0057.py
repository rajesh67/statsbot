# Generated by Django 2.0 on 2018-03-23 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0012_auto_20180324_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productprice',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='shopping.SearchProduct'),
        ),
        migrations.AlterField(
            model_name='searchproduct',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_products', to='shopping.Store'),
        ),
    ]
