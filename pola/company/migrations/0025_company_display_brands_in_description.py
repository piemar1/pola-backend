# Generated by Django 3.2.12 on 2022-04-04 17:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('company', '0024_auto_20211229_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='display_brands_in_description',
            field=models.BooleanField(
                choices=[(True, 'Tak'), (False, 'Nie')],
                default=False,
                verbose_name='Wyświetlaj informacje o markach w opisie',
            ),
        ),
    ]
