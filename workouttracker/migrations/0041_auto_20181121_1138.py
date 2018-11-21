# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-21 10:38
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workouttracker', '0040_auto_20181119_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exercisetype',
            options={'ordering': ['order']},
        ),
        # migrations.AddField(
        #     model_name='exercisetype',
        #     name='order',
        #     field=models.IntegerField(default=0),
        # ),
        migrations.AddField(
            model_name='musclegroup',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='workouttracker.ExerciseType'),
        ),
        migrations.AlterField(
            model_name='workoutsummary',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 21, 11, 38, 42, 248000)),
        ),
    ]
