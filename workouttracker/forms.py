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
            if field is not 'start':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
            else:
                pass

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
        fields = ['reps', 'sets']

class WorkoutSummaryForm(ModelForm):
    start = forms.DateTimeField(initial=datetime.now(), widget=AdminDateWidget())
    time = forms.DateTimeField(initial=datetime.now(), widget=AdminTimeWidget())

    class Meta:
        model = WorkoutSummary
        # fields = ['start', 'time', 'duration', 'calories', 'group', 'intensity', 'avg_heartrate', 'notes']
        fields = '__all__'
        # widgets = {
        #     'start': AdminDateWidget(),
        # }


ExerciseFormSet = forms.inlineformset_factory(WorkoutSummary, WorkoutDetail, form=WorkoutSummaryForm, extra=3)
