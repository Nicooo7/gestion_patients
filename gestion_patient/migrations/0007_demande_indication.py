# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-04 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_patient', '0006_auto_20171204_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='indication',
            field=models.CharField(default='vide', max_length=300, null=True),
        ),
    ]
