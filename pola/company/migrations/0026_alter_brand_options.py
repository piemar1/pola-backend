# Generated by Django 3.2.12 on 2022-04-17 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0025_company_display_brands_in_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['-name'], 'permissions': (), 'verbose_name': 'Marka', 'verbose_name_plural': 'Marki'},
        ),
    ]
