from django.forms import ModelForm
from django.forms import ModelChoiceField
from ..services.models import Config

class ConfigForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['algorithm'].widget.attrs.update({'required': True})
        self.fields['algorithm'].label = 'Algoritmo'
        self.fields['num_repl'].label = 'Replicas por índice'

    class Meta:
        model = Config
        fields = ['algorithm', 'num_repl', 'max_result_window']
