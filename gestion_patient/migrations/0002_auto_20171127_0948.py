# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_patient', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='injection',
            field=models.CharField(choices=[('oui', 'oui'), ('non', 'non'), ('ne sait pas', 'ne sait pas')], default='aucun', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='demande',
            name='degre_urgence',
            field=models.CharField(choices=[('H24', 'H24'), ('H48', 'H48'), ('J7', 'J7'), ('programmer', 'programmer')], max_length=10),
        ),
        migrations.AlterField(
            model_name='demande',
            name='type_examen',
            field=models.CharField(choices=[('scanner', 'scanner'), ('IRM', 'IRM'), ('echographie', 'echographie'), ('autre', 'autre')], max_length=10),
        ),
    ]