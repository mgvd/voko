# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0039_auto_20150719_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='finalized',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
