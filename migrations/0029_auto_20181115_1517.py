# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-15 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouttracker', '0028_auto_20181115_1024'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workoutsummary',
            options={'ordering': ['-start'], 'verbose_name_plural': 'Workout Summaries'},
        ),
        migrations.AddField(
            model_name='weighthistory',
            name='bodyfat',
            field=models.FloatField(default=20),
        ),
    ]