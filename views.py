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
import os
import csv
from django.db.models import Q

def one_rep_max(reps, weight):
    return round(weight * (36 / (37 - reps)), 2)

def date_to_string(date):
    return str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

def time_to_string(date):
    return str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)

def get_dates_from_request(request, offset=15):
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    if start_date == None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date()
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
        return redirect('%s?next=%s' % ('/user/login', request.path))

    user = request.user
    profile = user.workout_user

    # make sure the user has a workout profile
    try:
        workout_user = user.workout_user
        has_profile = True
    except:
        has_profile = False

    if user.id != 10:
        start_date, end_date = get_dates_from_request(request)
    else:
        start_date = datetime.datetime.strptime('2018-11-16', '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime('2018-12-16', '%Y-%m-%d').date()

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)
    groups = MuscleGroup.objects.filter(type_id=2).filter(display_in_list=1).all()
    all_groups = MuscleGroup.objects.filter(display_in_list=1).all()

    return render(request, "workouttracker/index.html", {'user': user, 'workouts': workouts, 'dates': summaries['dates'], 'minutes': summaries['minutes'], 'calories': summaries['calories'], 'start_date': date_to_string(start_date), 'end_date': date_to_string(end_date), 'groups': groups, 'has_profile': has_profile, 'profile':  profile, 'all_groups': all_groups})

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
    days = (end_date - start_date).days

    workouts = WorkoutSummary.summary_breakdown(user, start_date=start_date, end_date=end_date)

    return JsonResponse({'workouts':workouts, 'days': days})

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
    major_groups = MuscleGroup.objects.filter(display_in_list=1).order_by("area__order", "name")

    # make a list of all the major muscle groups
    muscle_groups = []
    full_body_workouts = []

    data_dict = {}

    # initialize our data dict
    for group in major_groups:
        if group.super_group == 0:
            data_dict[group.name] = {'minutes': [0] * len(dates), 'calories': [0] * len(dates), 'color': group.color, 'dates': dates}

    used_muscle_groups = []
    for i, date in enumerate(dates):
        date_str = date_to_string(date)

        if date_str in workouts:
            for workout in workouts[date_str]:
                # if it is part of a per group workout
                if workout.group.super_group == 0:
                    # if the group is not already in our list add it
                    if workout.group.name not in muscle_groups:
                        used_muscle_groups.append(workout.group.name)

                    data_dict[workout.group.name]['minutes'][i] += workout.duration
                    data_dict[workout.group.name]['calories'][i] += workout.calories

                # else if workout contains multiple groups
                else:
                    # get the summary info for the workout
                    total_time = workout.duration
                    total_reps = 0
                    for exercise in workout.workoutdetail_set.all():
                        total_reps += (exercise.reps * exercise.sets)

                    # loop through the exercises and use the main group of each
                    for exercise in workout.workoutdetail_set.all():
                        exercise_reps = (exercise.sets * exercise.reps)
                        exercise_percent = exercise_reps / total_reps
                        exercise.duration = total_time * exercise_percent
                        exercise.calories = workout.calories * exercise_percent

                        current_group = exercise.exercise.main_group.name
                        if current_group not in muscle_groups:
                            used_muscle_groups.append(current_group)

                        data_dict[current_group]['minutes'][i] += exercise.duration
                        data_dict[current_group]['calories'][i] += exercise.calories

    # clean up our list of groups
    for group in major_groups:
        if group.name in used_muscle_groups:
            muscle_groups.append(group.name)

    return JsonResponse({'dates': dates, 'groups': muscle_groups, 'data': data_dict }, safe=False)

def WorkoutDetails(request):
    user = request.user
    start_date, end_date = get_dates_from_request(request)

    workouts = WorkoutSummary.workouts_by_day(user=user, start_date=start_date, end_date=end_date)
    summaries = WorkoutSummary.summary_by_day(user=user, start_date=start_date, end_date=end_date)

    dates = summaries['dates']
    workouts_dict = {}
    for date in dates:
        workouts_dict[date] = []
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
        dict['exercise_id'] = workout.exercise.id
        dict['user_units'] = user.workout_user.unit_type
        data.append(dict)

    return JsonResponse(data, safe=False)

def WeightDetails(request):
    start_date, end_date = get_dates_from_request(request, offset=30)

    # add one day to the end_date since it is exclusive
    end_date = (end_date + datetime.timedelta(days=1))

    user = request.user
    units = user.workout_user.unit_type
    if units == "metric":
        unit_label = "kg"
    else:
        unit_label = "lbs"

    # create the list of dates so the plot is displayed correctly
    dates = []
    date = start_date
    while date < end_date:
        dates.append(date_to_string(date))
        date += datetime.timedelta(days=1)

    weights = WeightHistory.objects.filter(user=user).filter(datetime__gte=start_date).filter(datetime__lte=end_date)

    # initialize the dictionary to contain lists the length of dates of Null
    weight_dict = {'dates': dates, 'weights': [None] * len(dates), 'bodyfats': [None] * len(dates), 'units': [None] * len(dates), 'ids': [None] * len(dates)}
    for weight in weights:
        date_str = date_to_string(weight.datetime)
        idx = dates.index(date_str)

        if weight.bodyfat != 0:
            weight_dict['bodyfats'][idx] = weight.bodyfat

        weight_dict['units'][idx] = unit_label
        weight_dict['ids'][idx] = weight.id
        if weight.weight != 0:
            # make sure all weights are converted to users preferences
            if units == "metric" and weight.units == "lbs":
                weight_dict['weights'][idx] = round(weight.weight / 2.2, 1)
            elif units == "imp" and weight.units == "kg":
                weight_dict['weights'][idx] = round(weight.weight * 2.2, 1)
            else:
                weight_dict['weights'][idx] = round(weight.weight, 1)


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

    return JsonResponse({'groups': groups, 'workouts': workouts, 'tabular': tabular_dict, 'dates': dates, 'units': user.workout_user.unit_type}, safe=False)

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
            if user.id != 10:
                workout.save()

            # save the details
            details = exercise_form.save(commit=False)

            for detail in details:
                detail.workout = workout

                # handle unit conversion
                if user.workout_user.unit_type == "imp":
                    print("Converting...")
                    detail.units = "kgs"
                    detail.weight = detail.weight / 2.2

                if user.id != 10:
                    detail.save()

            return JsonResponse({'success': True, 'id': workout.id })
        else:
            return JsonResponse(form.errors)
    else:
        form = WorkoutSummaryForm(instance=workout, prefix="summary")
        exercise_form = ExerciseFormSet(instance=workout, prefix="detail")

    time = workout.start.strftime("%H:%M:%S")
    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout, 'date': date_to_string(workout.start), 'time': time, 'edit': True, 'profile': user.workout_user })

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
            if user.id != 10:
                workout.save()

            # save the details
            details = exercise_form.save(commit=False)

            for detail in details:
                detail.workout = workout

                # handle unit conversion
                if user.workout_user.unit_type == "imp":
                    detail.units = "kgs"
                    detail.weight = detail.weight / 2.2

                if user.id != 10:
                    detail.save()

            return JsonResponse({'success': True, 'id': workout.id})
        else:
            return JsonResponse(form.errors)
    else:
        form = WorkoutSummaryForm(instance=workout, prefix="summary")
        exercise_form = ExerciseFormSet(instance=workout, prefix="detail")

    time = datetime.datetime.now().strftime("%H:%M:%S")
    return render(request, 'workouttracker/workout_form.html', {'form': form, 'exercise_form': exercise_form, 'workout': workout, 'time': time, 'edit': False, 'profile': user.workout_user})

def DeleteWorkout(request, pk):
    user = request.user
    workout = WorkoutSummary.objects.filter(user=user).filter(pk=pk).first()
    if user.id != 10:
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

    units = user.workout_user.unit_type

    if new_weight:
        if id:
            weight = WeightHistory.objects.filter(user=user).filter(pk=id).first()
            new_date = datetime.datetime.strptime(request.POST.get("date"), '%Y-%m-%d')
            weight.datetime = new_date
        else:
            weight = WeightHistory()
            weight.datetime = datetime.datetime.now()
            weight.user = user

        if units == "imp":
            weight.weight = float(new_weight) / 2.2
            weight.units = "kg"
        else:
            weight.weight = new_weight

        if bodyfat:
            weight.bodyfat = bodyfat

        # we may want to use the previous body fat here to keep the chart looking nice
        else:
            pass

        if user.id != 10:
            weight.save()

        return JsonResponse({'success': True, 'weight': model_to_dict(weight)}, safe=False)

    return JsonResponse({'success': False})

def DeleteWeight(request, pk):
    user = request.user
    weight = WeightHistory.objects.filter(user=user).filter(pk=pk).first()
    if weight:
        if user.id != 10:
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
            if user.id != 10:
                user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if profile.unit_type == "imp":
                profile.height *= 2.54

            if user.id != 10:
                profile.save()

            return JsonResponse({'success': True})

        else:
            return JsonResponse(profile_form.errors)

    else:
        user_form = UserForm(instance=user, prefix="user")

        # handle the case if the user does not have an existing profile
        try:
            if user.workout_user.unit_type == "imp":
                user.workout_user.height = user.workout_user.height / 2.54

            profile_form = UserProfileForm(instance=user.workout_user, prefix="profile")
            msg = None
        except:
            profile_form = UserProfileForm(prefix="profile")
            msg = "Your gender, height, and age are required to calculate the calories burned during exercises. Please fill out this form."


    return render(request, 'workouttracker/profileForm.html', {'profile_form': profile_form, 'user_form': user_form, 'msg': msg, 'user': user })

def ExerciseByType(request, type):
    if type is not 0 and type is not 4:
        exercises = Exercise.objects.filter(Q(approved=1) | Q(approved=request.user.id)).filter(type_id=type).all().values()
    else:
        exercises = Exercise.objects.filter(Q(approved=1) | Q(approved=request.user.id)).all().values()


    return JsonResponse(list(exercises), safe=False)

def ExerciseByGroup(request, type, group):
    if int(group) == 22:
        exercises = Exercise.objects.all().values()
    else:
        exercises = Exercise.objects.filter(Q(type_id=type) & (Q(approved=1) | Q(approved=request.user.id)) & (Q(group=group) | Q(main_group=group))).filter().all().distinct().values()

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
            if exercise.exercise.name in workout_dict:
                workout_dict[exercise.exercise.name].append({'sets': exercise.sets, 'reps': exercise.reps, 'weight': exercise.weight,
                     'total_weight': (exercise.sets * exercise.reps * exercise.weight), 'workout_id': workout.id, 'exercise_id': exercise.exercise.id })
            else:
                workout_dict[exercise.exercise.name] = [{'sets': exercise.sets, 'reps': exercise.reps, 'weight': exercise.weight, 'total_weight': (exercise.sets * exercise.reps * exercise.weight), 'workout_id': workout.id, 'exercise_id': exercise.exercise.id }]

    return JsonResponse({'workouts': workout_dict, 'units': user.workout_user.unit_type })

def ExportData(request):
    user = request.user

    if user.is_authenticated:
        file_prefix = date_to_string(datetime.datetime.now()) + "_" + str(user.id)

        # export weight history
        weight_history = WeightHistory.objects.filter(user=user).order_by("datetime")
        weight_path = os.path.join(settings.MEDIA_ROOT, file_prefix + "_weights.csv")

        with open(weight_path, mode='w', newline='') as weight_file:
            weight_writer = csv.writer(weight_file, delimiter=str(u','), quotechar=str(u'"'), quoting=csv.QUOTE_MINIMAL)

            weight_writer.writerow(['Date', 'Weight', 'Units', 'Bodyfat'])

            for i, weight in enumerate(weight_history):
                weight_writer.writerow([weight.datetime.date(), weight.weight, weight.units, weight.bodyfat])

        # export workout summaries
        workouts = WorkoutSummary.objects.filter(user=user).order_by("start")

        summary_path = os.path.join(settings.MEDIA_ROOT, file_prefix + "_workout_summaries.csv")

        with open(summary_path, mode='w', newline='') as summary_file:
            summary_writer = csv.writer(summary_file, delimiter=str(u','), quotechar=str(u'"'), quoting=csv.QUOTE_MINIMAL)

            summary_writer.writerow(['id', 'date', 'type', 'group', 'duration', 'calories', 'intensity', 'avg_heartrate', 'notes'])

            for i, summary in enumerate(workouts):
                summary_writer.writerow([summary.id, date_to_string(summary.start), summary.type.name, summary.group.name, summary.duration, summary.calories, summary.intensity, summary.avg_heartrate, summary.notes])

        # export workout details
        details = WorkoutDetail.objects.filter(workout__user=user).order_by("workout__start")
        details_path = os.path.join(settings.MEDIA_ROOT, file_prefix + "_workout_details.csv")

        # detail_df = pd.DataFrame(columns=['workout_id', 'id', 'exercise', 'reps', 'sets', 'weight', 'units', 'duration', 'distance', 'intensity'])
        with open(details_path, mode='w', newline='') as detail_file:
            detail_writer = csv.writer(detail_file, delimiter=str(u','), quotechar=str(u'"'), quoting=csv.QUOTE_MINIMAL)

            detail_writer.writerow(['workout_id', 'id', 'exercise', 'reps', 'sets', 'weight', 'units', 'duration', 'distance', 'intensity'])

            for i, detail in enumerate(details):
                detail_writer.writerow([detail.workout_id, detail.id, detail.exercise.name, detail.reps, detail.sets, detail.weight, detail.units, detail.duration, detail.distance, detail.intensity])

        return JsonResponse({'prefix': file_prefix})

    else:
        return JsonResponse({'status': 'error'})

def HistoryByExercise(request, pk):
    start_date, end_date = get_dates_from_request(request, offset=30)

    # add one to the end date for inclusive
    end_date += datetime.timedelta(days=1)

    user = request.user
    workouts = WorkoutDetail.objects.filter(workout__user=user).filter(workout__start__gte=start_date).filter(workout__start__lte=end_date).filter(exercise_id=pk)

    # create our list of dates within the range
    dates = []
    current_date = start_date
    while (current_date < end_date):
        date = str(current_date.year) + "-" + str(current_date.month).zfill(2) + "-" + str(current_date.day).zfill(2)
        dates.append(date)
        current_date = (current_date + datetime.timedelta(days=1))

    # create a dict of workouts for that exercise
    workout_dict = {}
    for workout in workouts:
        date_str = date_to_string(workout.workout.start)

        dict = model_to_dict(workout)

        orm = one_rep_max(workout.reps, workout.weight)

        if date_str in workout_dict:
            workout_dict[date_str]['reps'] += (workout.reps * workout.sets)
            workout_dict[date_str]['sets'] += workout.sets
            workout_dict[date_str]['weight'] += workout.weight
            workout_dict[date_str]['time'] += workout.duration
            workout_dict[date_str]['total_weight'] += (workout.weight * workout.reps * workout.sets)
            workout_dict[date_str]['count'] += 1
            if workout.weight > workout_dict[date_str]['max_weight']:
                workout_dict[date_str]['max_weight'] = workout.weight
                workout_dict[date_str]['max_reps'] = workout.reps
            if orm > workout_dict[date_str]['one_rep_max']:
                workout_dict[date_str]['one_rep_max'] = orm

        else:
            workout_dict[date_str] = {'reps': workout.reps * workout.sets, 'time': workout.duration, 'one_rep_max': orm, 'sets': workout.sets, 'weight': workout.weight, 'total_weight': workout.weight * workout.reps * workout.sets, 'max_weight': workout.weight, 'count': 1}

    sets = []
    reps = []
    total_weights = []
    counts = []
    max_weights = []
    avg_weights = []
    one_rep_maxes = []
    durations = []

    # convert to lists by date
    for date in dates:
        if date in workout_dict:
            sets.append(workout_dict[date]['sets'])
            reps.append(workout_dict[date]['reps'])
            total_weights.append(workout_dict[date]['total_weight'])
            counts.append(workout_dict[date]['count'])
            max_weights.append(workout_dict[date]['max_weight'])
            avg_weights.append(workout_dict[date]['weight'] / (workout_dict[date]['count']))
            one_rep_maxes.append(workout_dict[date]['one_rep_max'])
            durations.append(workout_dict[date]['time'])
        else:
            sets.append(None)
            reps.append(None)
            total_weights.append(None)
            counts.append(None)
            max_weights.append(None)
            avg_weights.append(None)
            durations.append(None)
            one_rep_maxes.append(None)

    return JsonResponse({'dates': dates, 'duration': durations, 'exercises': workout_dict, 'sets': sets, 'reps': reps, 'avg_weights': avg_weights,  'total_weights': total_weights, 'counts': counts, 'max_weights': max_weights, 'one_rep_maxes': one_rep_maxes, 'units': user.workout_user.unit_type}, safe=False)


def ExercisesPerformed(request):
    start_date, end_date = get_dates_from_request(request, offset=30)

    # add one to the end date for inclusive
    end_date += datetime.timedelta(days=1)

    user = request.user
    workouts = WorkoutDetail.objects.filter(workout__user=user).filter(workout__start__gte=start_date).filter(workout__start__lte=end_date)

    exercises = []
    for workout in workouts:
        tuple = (workout.exercise.name, workout.exercise.id)

        if tuple not in exercises:
            exercises.append(tuple)

    exercises.sort()

    return JsonResponse({'exercises': exercises})

def AddExercise(request):
    if request.method == 'POST':
        exercise = Exercise()
        exercise.name = request.POST.get('name')
        exercise.main_group_id = request.POST.get('main_group')
        exercise.type_id = request.POST.get('type')
        exercise.approved = request.user.id

        # override the mets for stretching exercises, the rest we'll leave at default
        if exercise.type_id == 3:
            exercise.low_mets = 3
            exercise.med_mets = 4
            exercise.high_mets = 5

        if request.user.id != 10:
            exercise.save()

        return JsonResponse({'success': True, 'exercise': model_to_dict(exercise)})
    else:
        return JsonResponse({'success': False})
