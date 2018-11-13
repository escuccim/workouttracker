# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import MuscleGroup, WorkoutSummary, Exercise, WorkoutDetail, WeightHistory, BodyAreas
from .forms import MuscleGroupForm
from django.contrib.auth.models import User

class WorkoutDetailInline(admin.TabularInline):
    model = WorkoutDetail

class WorkoutAdmin(admin.ModelAdmin):
    inlines = [WorkoutDetailInline]

class GroupExerciseInline(admin.TabularInline):
    model = Exercise.group.through
    verbose_name_plural = "Exercises"

class GroupHierarchyInline(admin.TabularInline):
    model = MuscleGroup
    fk_name = "parent"
    verbose_name_plural = "Children"

class MuscleGroupAdmin(admin.ModelAdmin):
    form = MuscleGroupForm
    fieldsets = (
        (None, {
            'fields': ('name', 'color', 'area', 'parent')
            }),
        )
    inlines = [GroupHierarchyInline, GroupExerciseInline]
    ordering = ['parent_id', 'name']
    list_display = ['name', 'area', 'parent']

class ExerciseAdmin(admin.ModelAdmin):
    search_fields = ['name', 'group__name']
    list_display = ["name", "main_group"]

class BodyAreaInline(admin.TabularInline):
    model = MuscleGroup

class BodyAreaAdmin(admin.ModelAdmin):
    inlines = [BodyAreaInline]

# Register your models here.
admin.site.register(BodyAreas, BodyAreaAdmin)
admin.site.register(MuscleGroup, MuscleGroupAdmin)
admin.site.register(WorkoutSummary, WorkoutAdmin)
admin.site.register(WorkoutDetail)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(WeightHistory)
