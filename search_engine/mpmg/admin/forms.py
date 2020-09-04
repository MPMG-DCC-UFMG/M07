from django.forms import ModelForm
from django.forms import ModelChoiceField
from ..services.models import Config

class ConfigForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['algorithm'].label = 'Algoritmo'
        self.fields['num_repl'].label = 'Replicas por índice'
        self.fields['num_repl'].widget.attrs.update({'max': 10})
        self.fields['max_result_window'].widget.attrs.update({'min': 1})
        

    class Meta:
        model = Config
        fields = ['algorithm', 'num_repl', 'max_result_window']
