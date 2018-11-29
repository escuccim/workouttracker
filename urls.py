"""djangoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

app_name = "workout"

urlpatterns = [
    url(r'^$', views.Index, name="index"),
    url(r'^edit_workout/(?P<pk>\d+)', views.EditWorkoutSummary, name="edit_workout_form"),
    url(r'^profile', views.EditProfile, name="edit_profile"),
    url(r'^add_workout/', views.AddWorkoutSummary, name="add_workout_form"),
    url(r'^api/delete_workout/(?P<pk>\d+)', views.DeleteWorkout, name="delete_workout"),
    url(r'^api/chart_data', views.ChartData, name="chart_data"),
    url(r'^api/export_data', views.ExportData, name="export_data"),
    url(r'^api/chart_summary', views.ChartSummary, name="chart_summary"),
    url(r'^api/strength_data', views.StrengthData, name="strength_data"),
    url(r'^api/breakdown', views.ExerciseBreakdown, name="chart_breakdown"),
    url(r'^api/details', views.WorkoutDetails, name="workout_details"),
    url(r'^api/exercise_detail/(?P<id>\d+)', views.ExerciseDetails, name="exercise_detail"),
    url(r'^api/strength_detail/', views.StrengthDetails, name="strength_detail"),
    url(r'^api/exercise_by_type/(?P<type>\d+)', views.ExerciseByType, name="exercise_by_type"),
    url(r'^api/exercise_by_group/(?P<type>\d+)/(?P<group>\d+)', views.ExerciseByGroup, name="exercise_by_group"),
    url(r'^api/weight', views.WeightDetails, name="weight_detail"),
    url(r'^api/get_weight', views.GetWeight, name="get_last_weight"),
    url(r'^api/add_weight', views.AddWeight, name="add_weight"),
    url(r'^api/delete_weight/(?P<pk>\d+)', views.DeleteWeight, name="delete_weight"),
    url(r'^api/history_by_exercise/(?P<pk>\d+)', views.HistoryByExercise, name="history_by_exercise"),
    url(r'^api/exercises_performed', views.ExercisesPerformed, name="exercises_by_date"),
]
