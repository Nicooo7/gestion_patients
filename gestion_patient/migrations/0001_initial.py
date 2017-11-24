# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Demande',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prenom', models.CharField(max_length=30)),
                ('nom', models.CharField(max_length=30)),
                ('ipp', models.PositiveIntegerField()),
                ('degre_urgence', models.CharField(choices=[('H24', 'H24'), ('H48', 'H48'), ('J7', 'J7'), ('programmer', 'programmer')], default='programmer', max_length=2)),
                ('type_examen', models.CharField(max_length=30)),
            ],
        ),
    ]
