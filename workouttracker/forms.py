from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import MuscleGroup

class MuscleGroupForm(ModelForm):
    class Meta:
        model = MuscleGroup
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }