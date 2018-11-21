# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import numpy as np
import copy
import datetime

def calories_burned_walking(summary):
    user = UserProfile.objects.filter(user_id=summary.user_id).first()
    weight = WeightHistory.objects.filter(user_id=summary.user_id).last()

    # height and weight are required to use this method
    if user.height and weight:
        # calculate the total distance
        distance = 0
        for exercise in summary.workoutdetail_set.all():
            distance += exercise.distance

        kmh = distance / summary.duration
        mps = kmh / 3.6

        calories_burned = (0.035 * weight.weight) + ((mps ** 2) / user.height) * (0.029) * (weight.weight)
    else:
        calories_burned = calories_by_mets(summary)

    return calories_burned

def calories_burned_strength(summary):
    # get maximum heart rate
    user = UserProfile.objects.filter(user_id=summary.user_id).first()

    # if no heartrate was specified we will estimate it
    if summary.avg_heartrate == 0:
        if user.gender == "M":
            max_hr = (202 - (.55 * user.age))
        else:
            max_hr = (216 - (1.09 * user.age))

        # figure out the heart rate
        hr_multiplier = 0.5 + (summary.intensity * .075)

        hr_for_intensity = max_hr * hr_multiplier
    else:
        hr_for_intensity = summary.avg_heartrate

    weight = WeightHistory.objects.filter(user_id=summary.user_id).last()

    if user.gender == "M":
        calories_burned = ( (user.age * .2017) - (weight.weight * 0.09036) + (hr_for_intensity * 0.6309) - 55.0969 ) * summary.duration / 4.184
    else:
        calories_burned = ((user.age * 0.074) - (weight.weight * 0.05741) + (hr_for_intensity * 0.4472) - 20.4022) * summary.duration / 4.184

    return calories_burned

def calories_burned_cardio(summary):
    user = UserProfile.objects.filter(user_id=summary.user_id).first()

    # if no heartrate was specified we will estimate it
    if summary.avg_heartrate == 0:
        if user.gender == "M":
            max_hr = (202 - (.55 * user.age))
        else:
            max_hr = (216 - (1.09 * user.age))

        # figure out the heart rate
        hr_multiplier = 0.55 + (summary.intensity * .075)

        hr_for_intensity = max_hr * hr_multiplier
    # else we use the entered heart rate
    else:
        hr_for_intensity = summary.avg_heartrate

    weight = WeightHistory.objects.filter(user_id=summary.user_id).last()

    if user.gender == "M":
        calories_burned = ((-55.0969 + (0.6309 * hr_for_intensity) + (0.1988 * weight.weight) + (0.2017 * user.age))/4.184) * summary.duration
    else:
        calories_burned = ((-20.4022 + (0.4472 * hr_for_intensity) - (0.1263 * weight.weight) + (0.074 * user.age))/4.184) * summary.duration

    return calories_burned

def calories_for_exercise(exercise):
    # get the mets for the exercise
    if exercise.intensity == 0:
        mets = exercise.exercise.low_mets / 2
    elif exercise.intensity == 1:
        mets = exercise.exercise.low_mets
    elif exercise.intensity == 2:
        mets = exercise.exercise.med_mets
    elif exercise.intensity == 3:
        mets = exercise.exercise.high_mets

    # weight the mets by the duration or the number of total reps
    if exercise.reps != 0 and exercise.sets != 0:
        weight = exercise.reps * exercise.sets
    elif exercise.duration != 0:
        weight = exercise.duration
    else:
        weight = 1

    return mets, weight

def calories_by_mets(summary):
    # check if there are exercises associated with the workout
    exercise_set = summary.workoutdetail_set

    # if the summary has exercises we can use the mets to calculate the calories
    if exercise_set.first() != None:
        # get the info we need
        user = UserProfile.objects.filter(user_id=summary.user_id).first()
        base_mets = user.get_base_mets()

        # calculate the mets as an average of the mets for each
        # exercise at it's intensity
        exercise_count = 0
        mets_total = 0

        for exercise in exercise_set.all():
            exercise_mets, weight = calories_for_exercise(exercise)

            mets_total += exercise_mets * weight
            exercise_count += weight

        mets = mets_total / exercise_count

        calories_burned = mets * summary.duration * base_mets

    # else we will use a different method
    else:
        if summary.type_id == 2:
            calories_burned = calories_burned_strength(summary)
        elif summary.type_id == 5:
            calories_burned = calories_burned_walking(summary)
        elif summary.type_id == 1:
            calories_burned = calories_burned_cardio(summary)
        else:
            calories_burned = calories_burned_cardio(summary)

    return calories_burned


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="workout_user")
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), default="M")
    daily_target = models.IntegerField(default=30)
    height = models.FloatField(default=80)
    age = models.IntegerField(default=40)
    birthdate = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.user.first_name

    def get_base_mets(self):
        weight = WeightHistory.objects.filter(user_id=self.user_id).last()
        base_mets = 3.5 * weight.weight / 200
        return base_mets

    def save(self, *args, **kwargs):
        # calculate the age for the birthdate
        today = datetime.date.today()
        self.age = today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

        # save the relationship as normal
        super(UserProfile, self).save(*args, **kwargs)

class BodyAreas(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Body Areas"

class WeightHistory(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField()
    weight = models.FloatField(default=0)
    units = models.CharField(max_length=5, choices=(("kg","kg"), ("lbs", "lbs")))
    bodyfat = models.FloatField(default=0)

    class Meta:
        ordering = ['datetime']
        verbose_name = "Weight History"
        verbose_name_plural = "Weight Histories"

class MuscleGroup(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=12)
    parent = models.ForeignKey("MuscleGroup", on_delete=models.DO_NOTHING, blank=True, null=True)
    area = models.ForeignKey(BodyAreas, on_delete=models.DO_NOTHING, blank=True, null=True)
    type = models.ForeignKey("ExerciseType", on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ExerciseType(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['order']

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    main_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name="main_group", blank=True, null=True)
    group = models.ManyToManyField(MuscleGroup)
    low_mets = models.FloatField(default=3)
    med_mets = models.FloatField(default=5)
    high_mets = models.FloatField(default=7)
    type = models.ForeignKey(ExerciseType, on_delete=models.CASCADE, default=None, null=True)

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
    intensity = models.IntegerField(choices=((0, 'Very Low'), (1, 'Low'), (2, 'Moderate'), (3, 'High')), default=2)
    calories = models.FloatField(default=0)
    distance = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # calculate the calories burned during this exercise session
        exercise_mets, _ = calories_for_exercise(self)
        user = UserProfile.objects.filter(user_id=self.workout.user_id).first()
        base_mets = user.get_base_mets()

        calories_burned = exercise_mets * self.duration * base_mets

        self.calories = calories_burned

        # save the relationship as normal
        super(WorkoutDetail, self).save(*args, **kwargs)

        # update the parent summary with the new caloires
        self.summary.save()

    def __str__(self):
        return str(self.workout.start) + " - " + self.workout.group.name + " - " + self.exercise.name

    def __unicode__(self):
        return str(self.workout.start) + " - " + self.workout.group.name + " - " + self.exercise.name

    class Meta:
        pass

# Create your models here.
class WorkoutSummary(models.Model):
    start = models.DateTimeField(default=datetime.datetime.now())
    duration = models.IntegerField(default=0)
    type = models.ForeignKey(ExerciseType, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(MuscleGroup, on_delete=models.DO_NOTHING)
    calories = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    intensity = models.IntegerField(choices=((0, 'Very Low'), (1, 'Low'), (2, 'Moderate'), (3, 'High')), default=2)
    calculated_calories = models.IntegerField(default=0)
    avg_heartrate = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # calculate the calories burned during this exercise sesssion
        self.calculated_calories = calories_by_mets(self)

        if True:#self.calories == 0:
            self.calories = self.calculated_calories

        # save the relationship as normal
        super(WorkoutSummary, self).save(*args, **kwargs)

    @staticmethod
    def strength_training_history(user,  end_date=None, start_date=None, group=None):
        if start_date is None:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=15)).date()
        if end_date is None:
            end_date = datetime.datetime.now().date()

        end_date = (end_date + datetime.timedelta(days=1))

        workouts = WorkoutSummary.objects.filter(user=user).filter(type_id=2).filter(start__gte=start_date).filter(start__lte=end_date)

        if group is not None and group is not "":
            workouts = workouts.filter(group__name=group)

        workouts = workouts.order_by("start")

        workout_dict = {}
        groups = {}
        dates = []
        blanks = []

        # create our list of dates - we will show all dates, not just those where exercise was performed
        current_date = start_date
        while(current_date < end_date):
            date = str(current_date.year) + "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2)
            dates.append(date)
            current_date = (current_date + datetime.timedelta(days=1))
            blanks.append(None)

        # remove the last day since that is the day after the end of the period
        dates.pop()

        for workout in workouts:
            group = workout.group.name

            if group not in workout_dict:
                workout_dict[group] = {'avg_weight': copy.copy(blanks), 'max_weight': copy.copy(blanks), 'total_weight': copy.copy(blanks),'total_reps': copy.copy(blanks), 'total_sets': copy.copy(blanks)}
                groups[group] = workout.group.color

        for workout in workouts:
            exercises = workout.workoutdetail_set.all()
            date = str(workout.start.year) + "-" + str(workout.start.month).zfill(2) + "-" + str(workout.start.day).zfill(2)

            group = workout.group.name

            total_weight = 0
            total_sets = 0
            total_reps = 0
            weights = []

            for exercise in exercises:
                weights.append(exercise.weight)
                total_weight += (exercise.reps * exercise.sets * exercise.weight)
                total_sets += exercise.sets
                total_reps += exercise.sets * exercise.reps

            idx = dates.index(date)

            if len(weights):
                workout_dict[group]['max_weight'][idx] = np.max(weights)
                workout_dict[group]['avg_weight'][idx] = round(np.mean(weights), 2)

            workout_dict[group]['total_weight'][idx] = total_weight
            workout_dict[group]['total_sets'][idx] = total_sets
            workout_dict[group]['total_reps'][idx] = total_reps

        return workout_dict, groups, dates

    @staticmethod
    def workouts_by_day(user, end_date=None, start_date=None):
        if start_date is None:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        if end_date is None:
            end_date = datetime.datetime.now().date()

        end_date = (end_date + datetime.timedelta(days=1))

        workouts = WorkoutSummary.objects.filter(user=user).filter(start__gte=start_date).filter(start__lte=end_date)

        workout_dict = {}
        for workout in workouts:
            date = str(workout.start.year) + "-" + str(workout.start.month).zfill(2) + "-" + str(workout.start.day).zfill(2)

            if date not in workout_dict:
                workout_dict[date] = [workout]
            else:
                workout_dict[date].append(workout)

        return workout_dict

    @staticmethod
    def summary_by_day(user, end_date=None, start_date=None):
        if start_date is None:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        if end_date is None:
            end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()

        end_date = (end_date + datetime.timedelta(days=1))

        workouts = WorkoutSummary.objects.filter(user=user).filter(start__gte=start_date).filter(start__lte=end_date).order_by("-start")

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
        ordering = ['-start']
        verbose_name_plural = "Workout Summaries"