# Generated by Django 3.2.12 on 2022-04-17 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('company', '0026_alter_brand_options'),
        ('product', '0018_auto_20211229_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='company.brand',
                verbose_name='Marka produktu',
            ),
        ),
    ]
