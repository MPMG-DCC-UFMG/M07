from django.forms import ModelForm, Form
from django.forms import ModelChoiceField, BooleanField, IntegerField
from django.utils.translation import gettext_lazy as _
from ..services.models import Config, WeightedSearchFieldsConfigs, SearchableIndicesConfigs, SearchConfigs


class SearchConfigsForm(ModelForm):
    class Meta:  
        model = SearchConfigs  
        fields = "__all__"  

class AddWeightedSearchFieldForm(ModelForm):
    class Meta:  
        model = WeightedSearchFieldsConfigs  
        fields = "__all__"  

class EditWeightedSearchFieldForm(Form):
    weight = IntegerField(min_value = 1)
    searchable = BooleanField(required=False)

class AddSearchableIndexForm(ModelForm):
    class Meta:  
        model = SearchableIndicesConfigs  
        fields = "__all__"  

class EditSearchableIndexForm(Form):
    searchable = BooleanField(required=False)

class ConfigForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['algorithm'].label = 'Algoritmo'
        self.fields['num_repl'].label = 'Replicas por índice'
        self.fields['compare'].label = 'Conjunto de índices'
        
        # BM25
        self.fields['b'].widget.attrs.update({'class': 'bm25'})
        self.fields['k1'].widget.attrs.update({'class': 'bm25'})
        self.fields['discount_overlaps'].widget.attrs.update({'class': 'bm25'})
        
        # DFR
        self.fields['basic_model'].widget.attrs.update({'class': 'dfr'})
        self.fields['after_effect'].widget.attrs.update({'class': 'dfr'})
        self.fields['normalization_dfr'].widget.attrs.update({'class': 'dfr'})
        self.fields['normalization_parameter_dfr'].widget.attrs.update({'class': 'dfr'})
        
        # DFI
        self.fields['independence_measure'].widget.attrs.update({'class': 'dfi'})

        # IB
        self.fields['distribution'].widget.attrs.update({'class': 'ib'})
        self.fields['lambda_ib'].widget.attrs.update({'class': 'ib'})
        self.fields['normalization_ib'].widget.attrs.update({'class': 'ib'})
        self.fields['normalization_parameter_ib'].widget.attrs.update({'class': 'ib'})

        # LM Dirichlet
        self.fields['mu'].widget.attrs.update({'class': 'lmdirichlet'})

        # LM Jelinek Mercer
        self.fields['lambda_jelinek'].widget.attrs.update({'class': 'lmjelinekmercer'})

        self.fields['max_result_window'].widget.attrs.update({'min': 1})
        self.fields['normalization_dfr'].label = 'Normalização'
        self.fields['normalization_ib'].label = 'Normalização'
        self.fields['normalization_parameter_dfr'].label = 'Parâmetro de Normalização'
        self.fields['normalization_parameter_ib'].label = 'Parâmetro de Normalização'

        self.fields['lambda_jelinek'].label = 'λ'
        self.fields['lambda_ib'].label = 'λ'
        self.fields['mu'].label = 'μ'
        

    class Meta:
        model = Config
        # fields = '__all__'
        fields = ['compare',
                  'num_repl',
                  'max_result_window',
                  'algorithm', 
                  'k1', 
                  'b', 
                  'discount_overlaps', 
                  'normalization_dfr', 
                  'normalization_parameter_dfr',
                  'normalization_ib', 
                  'normalization_parameter_ib',
                  'basic_model',
                  'after_effect',
                  'independence_measure',
                  'lambda_jelinek',
                  'lambda_ib',
                  'mu',
                  'distribution']



        