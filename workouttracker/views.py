# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings
import io
import base64
import numpy as np
import datetime
from .models import WorkoutSummary, MuscleGroup, WorkoutDetail, WeightHistory
from .forms import WorkoutSummaryForm, ExerciseFormSet

def date_to_string(date):
    return str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

def time_to_string(date):
    return str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)

def get_dates_from_request(request, offset=7):
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    if start_date == None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=offset)).date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date == None:
        end_date = datetime.datetime.now().date()
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    return start_date, end_date

# convert a plot to a datastream
def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue())

# Create your views here.
def Index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    user = request.user
    start_date, end_date = get_dates_from_request(request)

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)

    return render(request, "workouttracker/index.html", {'user': user, 'workouts': workouts, 'dates': summaries['dates'], 'minutes': summaries['minutes'], 'calories': summaries['calories'], 'start_date': date_to_string(start_date), 'end_date': date_to_string(end_date)})

def ChartData(request):
    user = request.user
    # get our start and end dates from URL or default to one week up to and including today
    start_date, end_date = get_dates_from_request(request)

    # create a list of dates between start and end, inclusive
    dates = []
    date = start_date
    while date < end_date:
        dates.append(date)
        date += datetime.timedelta(days=1)
    dates.append(date)

    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)

    # get the total minutes and calories for each day in the dates
    calories_list = np.zeros_like(dates)
    minutes_list = np.zeros_like(dates)

    for i, date in enumerate(dates):
        date_str = date_to_string(date)
        if date_str in summaries['dates']:
            idx = summaries['dates'].index(date_str)
            calories_list[i] = summaries['calories'][idx]
            minutes_list[i] = summaries['minutes'][idx]

    return JsonResponse({'dates': dates, 'calories': list(calories_list), 'minutes': list(minutes_list)}, safe=False)

def ExerciseBreakdown(request):
    user = request.user
    # get our start and end dates from URL or default to one week up to and including today
    start_date, end_date = get_dates_from_request(request)

    # create a list of dates between start and end, inclusive
    dates = []
    date = start_date
    while date < end_date:
        dates.append(date)
        date += datetime.timedelta(days=1)
    dates.append(date)

    print(dates)

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    major_groups = MuscleGroup.objects.filter(parent_id=None).order_by("area__order", "name")

    # make a list of all the major muscle groups
    muscle_groups = []
    data_dict = {}
    for group in major_groups:
        muscle_groups.append(group.name)
        data_dict[group.name] = {'minutes': [], 'calories': [], 'color': group.color, 'dates': []}

        for i, date in enumerate(dates):
            date_str = date_to_string(date)
            found = False
            if date_str in workouts:
                for workout in workouts[date_str]:
                    if workout.group.name == group.name:
                        if date_str not in data_dict[group.name]['dates']:
                            data_dict[group.name]['minutes'].append(workout.duration)
                            data_dict[group.name]['calories'].append(workout.calories)
                            data_dict[group.name]['dates'].append(date_str)
                        # handle multiple occurences of same exercise on a day
                        else:
                            print("Duplicate group", group.name)
                            data_dict[group.name]['minutes'][i] += workout.duration
                            data_dict[group.name]['calories'][i] += workout.calories

                        found = True

            if not found:
                data_dict[group.name]['minutes'].append(0)
                data_dict[group.name]['calories'].append(0)
                data_dict[group.name]['dates'].append(date_str)

    # loop through the summaries and put them in day/group format


    return JsonResponse({'dates': dates, 'groups': muscle_groups, 'data': data_dict }, safe=False)

def WorkoutDetails(request):
    user = request.user
    start_date, end_date = get_dates_from_request(request)

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)

    dates = summaries['dates']
    workouts_dict = {}
    for date in dates:
        if date in workouts:
            for workout in workouts[date]:
                if date in workouts_dict:
                    workouts_dict[date].append({'id': workout.id, 'calories': workout.calories, 'time': time_to_string(workout.start), 'start': date_to_string(workout.start), 'minutes': workout.duration, 'group': workout.group.name})
                else:
                    workouts_dict[date] = [{'id': workout.id, 'calories': workout.calories, 'time': time_to_string(workout.start),  'start': date_to_string(workout.start), 'minutes': workout.duration, 'group': workout.group.name}]

    return JsonResponse({'dates': dates, 'summaries': summaries, 'workouts': workouts_dict }, safe=False)

def ExerciseDetails(request, id):
    user = request.user

    details = WorkoutDetail.objects.filter(workout_id=id).filter(workout__user_id=user.id)
    data = []

    for workout in details:
        dict = model_to_dict(workout)
        dict['exercise'] = workout.exercise.name
        data.append(dict)

    return JsonResponse(data, safe=False)

def WeightDetails(request):
    start_date, end_date = get_dates_from_request(request, offset=30)
    print(start_date)

    user = request.user
    weights = WeightHistory.objects.filter(user=user).filter(datetime__gte=start_date).filter(datetime__lte=end_date)

    weight_dict = {'dates': [], 'weights': [], 'bodyfats': []}
    for weight in weights:
        date_str = date_to_string(weight.datetime)
        weight_dict['dates'].append(date_str)
        weight_dict['weights'].append(weight.weight)
        weight_dict['bodyfats'].append(weight.bodyfat)

    return JsonResponse(weight_dict, safe=False)

def EditWorkoutSummary(request, pk):
    user = request.user
    workout = WorkoutSummary.objects.filter(user=request.user).get(id=pk)

    if request.method == 'POST':
        print(request.POST)
        form = WorkoutSummaryForm(request.POST, prefix="summary", instance=workout)
        exercise_form = ExerciseFormSet(request.POST, prefix="detail", instance=workout)

        if form.is_valid() and exercise_form.is_valid():
            # combine the date and time into one field
            date = form.cleaned_data["start"]
            time = form.cleaned_data['time']

            # save the summary
            workout = form.save(commit=False)
            workout.start = datetime.datetime.combine(date, time)
            workout.user_id = user.id
            workout.save()

            # save the details
            exercise_form.save()

            return JsonResponse({'success': True, 'id': workout.id })
        else:
            return JsonResponse(form.errors)
    else:
        form = WorkoutSummaryForm(instance=workout, prefix="summary")
        exercise_form = ExerciseFormSet(instance=workout, prefix="detail")


    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout, 'date': date_to_string(workout.start)})

def AddWorkoutSummary(request):
    user = request.user
    workout = WorkoutSummary()

    if request.method == 'POST':
        form = WorkoutSummaryForm(request.POST, prefix="summary")
        exercise_form = ExerciseFormSet(request.POST, prefix="detail", instance=workout)

        if form.is_valid() and exercise_form.is_valid():
            # combine the date and time into one field
            date = form.cleaned_data["start"]
            time = form.cleaned_data['time']

            # save the summary
            summary = form.save(commit=False)
            summary.start = datetime.datetime.combine(date, time)
            summary.user_id = user.id
            summary.save()
            print(summary)

            # save the details
            details = exercise_form.save(commit=False)
            for detail in details:
                detail.workout = summary
                detail.save()
        else:
            return JsonResponse(form.errors)
    else:
        form = WorkoutSummaryForm(instance=workout, prefix="summary")
        exercise_form = ExerciseFormSet(instance=workout, prefix="detail")


    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout})