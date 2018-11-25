# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-13 08:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workouttracker', '0012_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('weight', models.FloatField(default=0)),
                ('units', models.CharField(choices=[('kg', 'kg'), ('lbs', 'lbs')], max_length=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]