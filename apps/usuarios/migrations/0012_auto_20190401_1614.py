# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2019-04-01 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0011_egresados_generacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='minuta',
            name='lista_asistencia',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='minuta',
            name='puntos',
            field=models.TextField(blank=True),
        ),
    ]
