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
from .models import WorkoutSummary, MuscleGroup, WorkoutDetail, WeightHistory, Exercise
from .forms import WorkoutSummaryForm, ExerciseFormSet, UserProfileForm, UserForm, PasswordForm

def date_to_string(date):
    return str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

def time_to_string(date):
    return str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)

def get_dates_from_request(request, offset=15):
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    if start_date == None:
        start_date = (datetime.datetime.now()).replace(day=1).date()
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
        return redirect('%s?next=%s' % ('/en/user/login', request.path))

    user = request.user

    # make sure the user has a workout profile
    try:
        workout_user = user.workout_user
        has_profile = True
    except:
        has_profile = False

    start_date, end_date = get_dates_from_request(request)

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)
    groups = MuscleGroup.objects.filter(type_id=2).filter(parent_id=None).all()

    return render(request, "workouttracker/index.html", {'user': user, 'workouts': workouts, 'dates': summaries['dates'], 'minutes': summaries['minutes'], 'calories': summaries['calories'], 'start_date': date_to_string(start_date), 'end_date': date_to_string(end_date), 'groups': groups, 'has_profile': has_profile})

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

def ChartSummary(request):
    user = request.user
    # get our start and end dates from URL or default to one week up to and including today
    start_date, end_date = get_dates_from_request(request)

    workouts = WorkoutSummary.summary_breakdown(user, start_date=start_date, end_date=end_date)

    return JsonResponse(workouts)

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

    # add one day to the end_date since it is exclusive
    end_date = (end_date + datetime.timedelta(days=1))

    user = request.user
    weights = WeightHistory.objects.filter(user=user).filter(datetime__gte=start_date).filter(datetime__lte=end_date)

    weight_dict = {'dates': [], 'weights': [], 'bodyfats': [], 'units': [], 'ids': []}
    for weight in weights:
        date_str = date_to_string(weight.datetime)
        weight_dict['dates'].append(date_str)
        weight_dict['weights'].append(weight.weight)
        weight_dict['bodyfats'].append(weight.bodyfat)
        weight_dict['units'].append(weight.units)
        weight_dict['ids'].append(weight.id)

    return JsonResponse(weight_dict, safe=False)

def StrengthData(request):
    start_date, end_date = get_dates_from_request(request, offset=30)

    # add one day to the end_date since it is exclusive
    end_date = (end_date + datetime.timedelta(days=1))

    group = request.GET.get("group", None)

    # get the breakdown
    user = request.user
    workouts, groups, dates = WorkoutSummary.strength_training_history(user=user, start_date=start_date, end_date=end_date, group=group)

    # convert the data to a different format for the tabular report
    tabular_dict = {}
    for i, date in enumerate(dates):
        # add the date to the dictionary
        tabular_dict[date] = {}

        # loop through the workouts and if there is data for the data add it
        for group in workouts:
            if workouts[group]['avg_weight'][i] is not None:
                tabular_dict[date][group] = {
                    'avg_weight': workouts[group]['avg_weight'][i],
                    'max_weight': workouts[group]['max_weight'][i],
                    'total_sets': workouts[group]['total_sets'][i],
                    'total_reps': workouts[group]['total_reps'][i],
                    'total_weight': workouts[group]['total_weight'][i],
                }

    return JsonResponse({'groups': groups, 'workouts': workouts, 'tabular': tabular_dict, 'dates': dates}, safe=False)

def EditWorkoutSummary(request, pk):
    user = request.user
    workout = WorkoutSummary.objects.filter(user=request.user).get(id=pk)

    if request.method == 'POST':
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

    time = workout.start.strftime("%H:%M:%S")
    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout, 'date': date_to_string(workout.start), 'time': time, 'edit': True})

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
            workout = form.save(commit=False)
            workout.start = datetime.datetime.combine(date, time)
            workout.user_id = user.id
            workout.save()

            # save the details
            details = exercise_form.save(commit=False)
            for detail in details:
                detail.workout = workout
                detail.save()

            return JsonResponse({'success': True, 'id': workout.id})
        else:
            return JsonResponse(form.errors)
    else:
        form = WorkoutSummaryForm(instance=workout, prefix="summary")
        exercise_form = ExerciseFormSet(instance=workout, prefix="detail")

    time = datetime.datetime.now().strftime("%H:%M:%S")
    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout, 'time': time, 'edit': False})

def DeleteWorkout(request, pk):
    user = request.user
    workout = WorkoutSummary.objects.filter(user=user).filter(pk=pk).first()
    workout.delete()

    return JsonResponse({'success': True})

def GetWeight(request):
    user = request.user
    weight = user.weighthistory_set.order_by('datetime').last()

    date = date_to_string(weight.datetime)
    weight = model_to_dict(weight)
    weight['date'] = date

    return JsonResponse(weight, safe=False)

def AddWeight(request):
    user = request.user
    bodyfat = request.POST.get("bodyfat", None)
    new_weight = request.POST.get("weight")
    id = request.POST.get("id")

    if new_weight:
        if id:
            weight = WeightHistory.objects.filter(user=user).filter(pk=id).first()
            new_date = datetime.datetime.strptime(request.POST.get("date"), '%Y-%m-%d')
            weight.datetime = new_date
        else:
            weight = WeightHistory()
            weight.datetime = datetime.datetime.now()
            weight.user = user

        weight.weight = new_weight
        weight.units = "kg"

        if bodyfat:
            weight.bodyfat = bodyfat
        # we may want to use the previous body fat here to keep the chart looking nice
        else:
            pass

        weight.save()

        return JsonResponse({'success': True, 'weight': model_to_dict(weight)}, safe=False)

    return JsonResponse({'success': False})

def DeleteWeight(request, pk):
    user = request.user
    weight = WeightHistory.objects.filter(user=user).filter(pk=pk).first()
    if weight:
        weight.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

def EditProfile(request):
    user = request.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, prefix="user", instance=user)

        # handle the case if the user does not have an existing profile
        try:
            profile_form = UserProfileForm(request.POST, prefix="profile", instance=user.workout_user)
            new_user = False
        except:
            profile_form = UserProfileForm(request.POST, prefix="profile")
            new_user = True

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()

            if not new_user:
                profile_form.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

            return JsonResponse({'success': True})

        else:
            return JsonResponse(profile_form.errors)

    else:
        user_form = UserForm(instance=user, prefix="user")

        # handle the case if the user does not have an existing profile
        try:
            profile_form = UserProfileForm(instance=user.workout_user, prefix="profile")
            msg = None
        except:
            profile_form = UserProfileForm(prefix="profile")
            msg = "Your gender, height, and age are required to calculate the calories burned during exercises. Please fill out this form."


    return render(request, 'workouttracker/profileForm.html', {'profile_form': profile_form, 'user_form': user_form, 'msg': msg})

def ExerciseByType(request, type):
    if type is not 0 and type is not 4:
        exercises = Exercise.objects.filter(type_id=type).all().values()
    else:
        exercises = Exercise.objects.all().values()


    return JsonResponse(list(exercises), safe=False)

def ExerciseByGroup(request, type, group):
    exercises = Exercise.objects.filter(type_id=type).filter(main_group_id=group).all().values()

    return JsonResponse(list(exercises), safe=False)

def StrengthDetails(request):
    user = request.user
    date = request.GET.get("date", None)
    group = request.GET.get("group", None)

    if date is None or group is None:
        return JsonResponse({'error': True})
    else:
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        end_date = start_date + datetime.timedelta(days=1)

    workouts = WorkoutSummary.objects.filter(user=user).filter(start__gte=start_date).filter(start__lte=end_date).filter(group__name=group)

    workout_dict = {}
    for workout in workouts:
        exercises = workout.workoutdetail_set.all()
        for exercise in exercises:
            workout_dict[exercise.exercise.name] = {'sets': exercise.sets, 'reps': exercise.reps, 'weight': exercise.weight, 'total_weight': (exercise.sets * exercise.reps * exercise.weight)}

    return JsonResponse(workout_dict)