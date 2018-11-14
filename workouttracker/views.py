# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import io
import base64
import numpy as np
import datetime
from .models import WorkoutSummary, MuscleGroup

def date_to_string(date):
    return str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

# convert a plot to a datastream
def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue())

# Create your views here.
def Index(request):
    user = request.user
    workouts = WorkoutSummary.workouts_by_day(user=user)
    summaries = WorkoutSummary.summary_by_day(user=user)

    start_date = request.GET.get('start', (datetime.datetime.now() - datetime.timedelta(days=7)).date())
    end_date = request.GET.get('end', datetime.datetime.now().date())

    return render(request, "workouttracker/index.html", {'user': user, 'workouts': workouts, 'dates': summaries['dates'], 'minutes': summaries['minutes'], 'calories': summaries['calories'], 'start_date': date_to_string(start_date), 'end_date': date_to_string(end_date)})

def ChartData(request):
    user = request.user
    # get our start and end dates from URL or default to one week up to and including today
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    if start_date == None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date == None:
        end_date = datetime.datetime.now().date()
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # create a list of dates between start and end, inclusive
    dates = []
    date = start_date
    while date < end_date:
        dates.append(date)
        date += datetime.timedelta(days=1)
    dates.append(date)

    summaries = WorkoutSummary.summary_by_day(user=user)

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
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    if start_date == None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date == None:
        end_date = datetime.datetime.now().date()
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # create a list of dates between start and end, inclusive
    dates = []
    date = start_date
    while date < end_date:
        dates.append(date)
        date += datetime.timedelta(days=1)
    dates.append(date)

    print(dates)

    workouts = WorkoutSummary.workouts_by_day(user=user)
    major_groups = MuscleGroup.objects.filter(parent_id=None).order_by("area__order", "name")

    # make a list of all the major muscle groups
    muscle_groups = []
    data_dict = {}
    for group in major_groups:
        muscle_groups.append(group.name)
        data_dict[group.name] = {'minutes': [], 'calories': [], 'color': group.color}

        for date in dates:
            date_str = date_to_string(date)
            found = False
            if date_str in workouts:
                for workout in workouts[date_str]:
                    if workout.group.name == group.name:
                        data_dict[group.name]['minutes'].append(workout.duration)
                        data_dict[group.name]['calories'].append(workout.calories)
                        found = True

            if not found:
                data_dict[group.name]['minutes'].append(0)
                data_dict[group.name]['calories'].append(0)

    # loop through the summaries and put them in day/group format


    return JsonResponse({'dates': dates, 'groups': muscle_groups, 'data': data_dict }, safe=False)