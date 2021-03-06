# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0022_auto_20141205_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit_of_measurement',
            field=models.CharField(max_length=10, choices=[(b'Stuk', b'Stuk'), (b'Gram', b'Gram'), (b'Decagram', b'Decagram (10g)'), (b'Hectogram', b'Hectogram (100g)'), (b'Half pond', b'Halve pond (250g)'), (b'Pond', b'Pond (500g)'), (b'Kilogram', b'Kilogram'), (b'Deciliter', b'Deciliter (100ml)'), (b'Liter', b'Liter')]),
            preserve_default=True,
        ),
    ]
