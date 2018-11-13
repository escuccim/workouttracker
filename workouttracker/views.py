# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import io
import base64
import numpy as np
import datetime
from .models import WorkoutSummary

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

    return render(request, "workouttracker/index.html", {'user': user, 'workouts': workouts, 'dates': summaries['dates'], 'minutes': summaries['minutes'], 'calories': summaries['calories']})

def ChartData(request):
    user = request.user
    # get our start and end dates from URL or default to one week up to and including today
    start_date = request.GET.get('start', (datetime.datetime.now() - datetime.timedelta(days=7)).date())
    end_date = request.GET.get('end', datetime.datetime.now().date())

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

    for date in dates:
        date_str = str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)
        idx = summaries['dates'].index(date_str)
        calories_list[idx] = summaries['calories'][idx]
        minutes_list[idx] = summaries['minutes'][idx]

    return JsonResponse({'dates': dates, 'calories': list(calories_list), 'minutes': list(minutes_list)}, safe=False)