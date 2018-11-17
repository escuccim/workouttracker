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
            if field is not 'start' and field is not 'time':
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
        fields = ['exercise', 'reps', 'sets', 'weight', 'intensity', 'duration']
        widgets = {
            'exercise': forms.Select(attrs={'style': 'width: 100%'}),
            'intensity': forms.Select(attrs={'style': 'width: 100%;'}),
            'reps': forms.TextInput(attrs={'size': 3}),
            'sets': forms.TextInput(attrs={'size': 3}),
            'weight': forms.TextInput(attrs={'size': 4}),
            'duration': forms.TextInput(attrs={'style': 'width: 100%;'}),
        }
class WorkoutSummaryForm(BootstrapModelForm):
    start = forms.DateTimeField(widget=AdminDateWidget())
    time = forms.TimeField(initial=datetime.now().time(), widget=AdminTimeWidget())

    class Meta:
        model = WorkoutSummary
        fields = ['start', 'time',  'group', 'duration', 'intensity', 'calories', 'avg_heartrate', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2})
        }

ExerciseFormSet = forms.inlineformset_factory(WorkoutSummary, WorkoutDetail, form=WorkoutDetailForm, extra=4, can_delete=True)