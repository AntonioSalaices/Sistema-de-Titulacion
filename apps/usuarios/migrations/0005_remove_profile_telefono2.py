# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2018-06-06 16:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_remove_profile_tipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='telefono2',
        ),
    ]
