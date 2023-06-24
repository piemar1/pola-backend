# Generated by Django 2.0.3 on 2018-05-27 06:40

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('pola', '0005_auto_20171225_1632'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='query',
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=['timestamp'], name='pola_query_timesta_ea44b7_brin', pages_per_range=64
            ),
        ),
    ]
