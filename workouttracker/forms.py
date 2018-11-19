from django.forms import ModelForm
from django import forms
from datetime import datetime
from django.forms.widgets import TextInput, SplitDateTimeWidget, SelectDateWidget
from .models import MuscleGroup, WorkoutSummary, WorkoutDetail
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

class BootstrapModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class MuscleGroupForm(ModelForm):
    class Meta:
        model = MuscleGroup
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

class WorkoutDetailForm(ModelForm):

    class Meta:
        model = WorkoutDetail
        fields = ['exercise', 'sets', 'reps', 'weight', 'intensity', 'duration', 'distance']
        widgets = {
            'exercise': forms.Select(attrs={'style': 'width: 100%', 'class': 'form-control'}),
            'intensity': forms.Select(attrs={'style': 'width: 100%;', 'class': 'form-control'}),
            'distance': forms.NumberInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'reps': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'sets': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'style': 'width: 100%;', 'min': 0, 'class': 'form-control'}),
        }

class WorkoutSummaryForm(BootstrapModelForm):
    time = forms.TimeField(initial=datetime.now().time(), widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = WorkoutSummary
        fields = ['start', 'time',  'type', 'group', 'duration', 'intensity', 'calories', 'avg_heartrate', 'notes']
        widgets = {
            'start': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2})
        }

ExerciseFormSet = forms.inlineformset_factory(WorkoutSummary, WorkoutDetail, form=WorkoutDetailForm, extra=4, can_delete=True)