# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 07:07
from __future__ import unicode_literals

from django.db import migrations, models


def set_to_true(apps, _):
    OrderRound = apps.get_model("ordering", "OrderRound")

    for oround in OrderRound.objects.all():
        print(oround.pk)
        oround.reminder_sent = True
        oround.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0071_auto_20170502_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderround',
            name='reminder_sent',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.RunPython(set_to_true)

    ]
