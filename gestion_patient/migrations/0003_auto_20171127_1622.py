# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_patient', '0002_auto_20171127_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='realisation',
            field=models.CharField(choices=[('oui', 'oui'), ('non', 'non')], default='non', max_length=10),
        ),
        migrations.AddField(
            model_name='demande',
            name='suppression',
            field=models.CharField(choices=[('oui', 'oui'), ('non', 'non')], default='non', max_length=10),
        ),
    ]
