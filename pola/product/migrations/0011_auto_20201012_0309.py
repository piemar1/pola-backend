# Generated by Django 2.0.2 on 2020-10-12 01:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('product', '0010_product_brand'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={
                'ordering': ['-created_at'],
                'permissions': (),
                'verbose_name': 'Produkt',
                'verbose_name_plural': 'Produkty',
            },
        ),
    ]
