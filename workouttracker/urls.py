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
    url(r'^add_workout/', views.AddWorkoutSummary, name="add_workout_form"),
    url(r'^api/chart_data', views.ChartData, name="chart_data"),
    url(r'^api/breakdown', views.ExerciseBreakdown, name="chart_breakdown"),
    url(r'^api/details', views.WorkoutDetails, name="workout_details"),
    url(r'^api/exercise_detail/(?P<id>\d+)', views.ExerciseDetails, name="exercise_detail"),
    url(r'^api/weight', views.WeightDetails, name="weight_detail"),
]
