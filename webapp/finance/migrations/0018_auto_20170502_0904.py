# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 07:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0017_auto_20161024_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='type',
            field=models.CharField(choices=[('CR', 'Credit'), ('DR', 'Debit')], db_index=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='payment',
            name='succeeded',
            field=models.BooleanField(default=False, help_text='Payment was validated by PSP'),
        ),
    ]
