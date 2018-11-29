from django.forms import ModelForm
from django import forms
from datetime import datetime
from django.forms.widgets import TextInput, SplitDateTimeWidget, SelectDateWidget
from .models import MuscleGroup, WorkoutSummary, WorkoutDetail, UserProfile
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from django.contrib.auth.models import User

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
            'exercise': forms.Select(attrs={'style': 'width: 100%', 'class': 'form-control exercise-list'}),
            'intensity': forms.Select(attrs={'style': 'width: 100%;', 'class': 'form-control'}),
            'distance': forms.NumberInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'reps': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'sets': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'size': 3, 'min': 0, 'style': 'width: 100%;', 'class': 'form-control weight_field'}),
            'duration': forms.TextInput(attrs={'style': 'width: 100%;', 'min': 0, 'class': 'form-control'}),
        }

class WorkoutSummaryForm(BootstrapModelForm):
    time = forms.TimeField(initial=datetime.now().time(), widget=forms.TimeInput(attrs={'type': 'time', 'step': 1}))

    def __init__(self, *args, **kwargs):
        super(WorkoutSummaryForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = self.fields['group'].queryset.filter(parent_id=None)

    class Meta:
        model = WorkoutSummary
        fields = ['start', 'time',  'type', 'group', 'duration', 'intensity', 'calories', 'avg_heartrate', 'notes']
        widgets = {
            'start': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'calories': forms.NumberInput(attrs={'disabled': True})

        }

class UserProfileForm(BootstrapModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'birthdate', 'unit_type', 'height']

        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date', 'required': 'true'}),
            'height': forms.NumberInput(attrs={'min': 120, 'max': 213})
        }

        labels = {
            'unit_type': 'Units',
            'birthdate': 'Date of Birth',
        }

class UserForm(BootstrapModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class PasswordForm(BootstrapModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput(), label="Old Password", required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password", required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password", required=False)

    def clean(self):
        # clean the data
        cleaned_data = super(PasswordForm, self).clean()

        # check that the passwords match
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            msg = "Your passwords do not match"
            self.add_error('new_password', msg)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password', ]

ExerciseFormSet = forms.inlineformset_factory(WorkoutSummary, WorkoutDetail, form=WorkoutDetailForm, extra=4, can_delete=True)