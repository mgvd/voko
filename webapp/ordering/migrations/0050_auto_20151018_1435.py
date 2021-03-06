# -*- coding: utf-8 -*-


from django.db import models, migrations
from ordering.core import find_unit


def convert_units(apps, schema_editor):
    Product = apps.get_model("ordering", "Product")
    ProductUnit = apps.get_model("ordering", "ProductUnit")

    for p in Product.objects.all():
        old_unit = p.unit_of_measurement

        try:
            amount, new_unit = find_unit(old_unit)
        except RuntimeError:
            amount = 1
            new_unit = ProductUnit.objects.get(name="Stuk")

        new_unit = ProductUnit.objects.get(id=new_unit.id)

        p.temp_unit = new_unit
        p.unit_amount = amount

        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0049_product_temp_unit'),
    ]

    operations = [
        migrations.RunPython(convert_units)
    ]
