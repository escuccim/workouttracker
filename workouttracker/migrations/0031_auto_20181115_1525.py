# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-15 14:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workouttracker', '0030_auto_20181115_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weighthistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]