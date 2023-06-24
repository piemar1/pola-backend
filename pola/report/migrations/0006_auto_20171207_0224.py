# Generated by Django 1.11.8 on 2017-12-07 01:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('report', '0005_auto_20171207_0215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={
                'get_latest_by': 'created_at',
                'ordering': ['-created_at'],
                'permissions': (('view_report', 'Can see all report'),),
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
    ]
