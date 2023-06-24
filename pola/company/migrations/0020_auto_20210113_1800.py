# Generated by Django 3.1.2 on 2021-01-13 17:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('company', '0019_auto_20201012_0309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                unique=False,
                verbose_name='Nazwa (pobrana z ILiM)',
            ),
        ),
    ]
