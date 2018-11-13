# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict

class BodyAreas(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Body Areas"

class WeightHistory(models.Model):
    user = models.OneToOneField(User)
    datetime = models.DateTimeField()
    weight = models.FloatField(default=0)
    units = models.CharField(max_length=5, choices=(("kg","kg"), ("lbs", "lbs")))

    class Meta:
        ordering = ['datetime']
        verbose_name = "Weight History"
        verbose_name_plural = "Weight Histories"

class MuscleGroup(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=12)
    parent = models.ForeignKey("MuscleGroup", on_delete=models.DO_NOTHING, blank=True, null=True)
    area = models.ForeignKey(BodyAreas, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    main_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name="main_group", blank=True, null=True)
    group = models.ManyToManyField(MuscleGroup)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class WorkoutDetail(models.Model):
    workout = models.ForeignKey("WorkoutSummary", on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.IntegerField(default=0)
    sets = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
    duration = models.FloatField(default=0)

    def __str__(self):
        return str(self.workout.start) + " - " + self.workout.group.name + " - " + self.exercise.name

    def __unicode__(self):
        return str(self.workout.start) + " - " + self.workout.group.name + " - " + self.exercise.name

    class Meta:
        pass

# Create your models here.
class WorkoutSummary(models.Model):
    start = models.DateTimeField()
    duration = models.IntegerField(default=0)
    group = models.ForeignKey(MuscleGroup, on_delete=models.DO_NOTHING)
    calories = models.IntegerField(default=0)
    user = models.ForeignKey(User)

    @staticmethod
    def workouts_by_day(user):
        workouts = WorkoutSummary.objects.filter(user=user)

        workout_dict = {}
        for workout in workouts:
            date = str(workout.start.year) + "-" + str(workout.start.month).zfill(2) + "-" + str(workout.start.day).zfill(2)

            if date not in workout_dict:
                workout_dict[date] = [workout]
            else:
                workout_dict[date].append(workout)

        return workout_dict

    @staticmethod
    def summary_by_day(user):
        workouts = WorkoutSummary.objects.filter(user=user)

        dates = []
        calories = []
        minutes = []
        workout_dict = {}

        for workout in workouts:
            date = str(workout.start.year) + "-" + str(workout.start.month).zfill(2) + "-" + str(workout.start.day).zfill(2)

            if date not in dates:
                calories.append(workout.calories)
                minutes.append(workout.duration)
            else:
                calories[-1] += workout.calories
                minutes[-1] += workout.duration

            if date not in dates:
                dates.append(date)

        return { 'dates': dates, 'calories': calories, 'minutes': minutes }

    def __str__(self):
        return str(self.start) + " - " + self.group.name

    def __unicode__(self):
        return str(self.start) + " - " + self.group.name

    class Meta:
        ordering = ['start']
        verbose_name_plural = "Workout Summaries"