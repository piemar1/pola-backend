# Generated by Django 3.1.2 on 2021-01-13 17:03

from django.db import migrations

SQL_STATEMENT = """
INSERT INTO product_product_companies(product_id, company_id)
SELECT product_product.id AS product_id,
       product_product.company_id AS company_id
FROM product_product
WHERE product_product.company_id IS NOT NULL;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_auto_20210117_0109'),
    ]

    operations = [
        migrations.RunSQL(SQL_STATEMENT),
    ]