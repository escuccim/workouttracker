# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-14 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouttracker', '0016_auto_20181113_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='bodyareas',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
