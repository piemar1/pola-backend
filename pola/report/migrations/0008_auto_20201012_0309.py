# Generated by Django 2.0.2 on 2020-10-12 01:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('report', '0007_auto_20180527_0848'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={
                'get_latest_by': 'created_at',
                'ordering': ['-created_at'],
                'permissions': (),
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
    ]
