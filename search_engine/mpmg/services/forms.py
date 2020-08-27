from django.forms import ModelForm
from django.forms import ModelChoiceField
from .models import Config

class ConfigForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['algorithm'].widget.attrs.update({'required': True})
        self.fields['algorithm'].label = 'Algoritmo'

    class Meta:
        model = Config
        fields = ['algorithm']
