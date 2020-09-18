import json
import elasticsearch
import elasticsearch_dsl
import requests
import traceback
import sys
from elasticsearch import helpers
from django.conf import settings

class Elastic:
    def __init__(self):
        super().__init__()
        self.ELASTIC_ADDRESS = settings.ELASTICSEARCH_DSL['default']['hosts']
        self.es = elasticsearch.Elasticsearch([self.ELASTIC_ADDRESS], timeout=120)
        self.dsl = elasticsearch_dsl
        self.helpers = helpers
    
    def close_then_modify(self, index, body):
        """
        Função helper para alterar configurações estáticas que requerem o fechamento do índice.
        `<https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-update-settings.html>`_
        :arg index: Índice onde a modificação deve ser feita.
        :arg body: Configurações a modificar.
        """
        self.es.indices.close(index)
        resp = self.es.indices.put_settings(body=body, index=index)
        self.es.indices.open(index)
        return resp

    def get_cur_algo(self):
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = self.es.indices.get_settings(index=index, name='*sim*')
            try:
                sim = resp[index]['settings']['index']['similarity']['default']['type']
            except:
                sim = "BM25" # Default value
        return sim

    def set_cur_algo(self, **kwargs):
        algo = kwargs.get('algorithm')
        for index in settings.SEARCHABLE_INDICES.keys():
            cur_settings = self.es.indices.get_settings(index=index, name='*sim*')
            body = {'similarity': {'default': {}}}
            
            if cur_settings: 
                # Se houver configuração prévia, é necessário "limpar" as configurações de similaridade 
                # já definidas anteriormente. Para tal, o ES requer que definamos todas as configurações
                # (e apenas elas) já atribuídas a outros modelos como null.
                for setting, value in cur_settings[index]['settings']['index']['similarity']['default'].items():
                    if type(value) == dict:
                        for sub_setting in value.keys():
                            body['similarity']['default']['{}.{}'.format(setting, sub_setting)] = None
                    else:
                        body['similarity']['default'][setting] = None

            body['similarity']['default']['type'] = algo
            if algo == 'BM25':
                k1 = kwargs.get('k1', '1.2')
                b = kwargs.get('b', '0.75')
                discount_overlaps = kwargs.get('discount_overlaps', False)

                body['similarity']['default']['k1'] = k1
                body['similarity']['default']['b'] = b
                body['similarity']['default']['discount_overlaps'] = discount_overlaps
            
            elif algo == 'DFR':
                basic_model = kwargs.get('basic_model', 'g')
                after_effect = kwargs.get('after_effect', 'l')
                normalization = kwargs.get('normalization_dfr', 'h2')

                body['similarity']['default']['basic_model'] = basic_model
                body['similarity']['default']['after_effect'] = after_effect
                body['similarity']['default']['normalization'] = normalization
                
                # Regularization parameter
                parameter = 'c'
                default_param_value = '1.0'
                if normalization == 'h3':
                    default_param_value = '800.0'
                elif normalization == 'z':
                    parameter = 'z'
                    default_param_value = '0.3'

                normalization_param = kwargs.get('normalization_parameter_dfr', default_param_value)
                body['similarity']['default']['normalization.{}.{}'.format(normalization, parameter)] = normalization_param

            elif algo == 'DFI':
                independence_measure = kwargs.get('independence_measure', 'standardized')
                body['similarity']['default']['independence_measure'] = independence_measure

            elif algo == 'IB':
                distribution = kwargs.get('distribution', 'll')
                lamb = kwargs.get('lambda_ib', 'df')
                normalization = kwargs.get('normalization_ib', 'h2')

                body['similarity']['default']['distribution'] = distribution
                body['similarity']['default']['lambda'] = lamb
                body['similarity']['default']['normalization'] = normalization

                # Regularization parameter
                parameter = 'c'
                default_param_value = '1.0'
                if normalization == 'h3':
                    default_param_value = '800.0'
                elif normalization == 'z':
                    parameter = 'z'
                    default_param_value = '0.3'

                normalization_param = kwargs.get('normalization_parameter_ib', default_param_value)
                body['similarity']['default']['normalization.{}.{}'.format(normalization, parameter)] = normalization_param

            elif algo == 'LMDirichlet':
                mu = kwargs.get('mu', '2000.0')
                body['similarity']['default']['mu'] = mu

            elif algo == 'LMJelinekMercer':
                lamb = kwargs.get('lambda_jelinek', '0.1')
                body['similarity']['default']['lambda'] = lamb

            else:
                print('Algoritmo de ranqueamento inválido para o índice {}'.format(index))
            
            try:
                resp = self.close_then_modify(index, body)
            except:
                traceback.print_exc(file=sys.stdout)
                print('Não foi possível alterar o algoritmo de ranqueamento {} para o índice {}'.format(algo, index))
                resp = {'acknowledged': False}
            
        return resp

    def get_cur_replicas(self):
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = self.es.indices.get_settings(index=index, name='*replicas')
            try:
                num_repl = resp[index]['settings']['index']['number_of_replicas']
            except:
                print('Não foi possível encontrar o número de replicas para o índice {}'.format(index))
                resp = {'acknowledged': False}
        return num_repl
    
    def set_cur_replicas(self, value):
        for index in settings.SEARCHABLE_INDICES.keys():
            try:
                resp = self.es.indices.put_settings(body={'number_of_replicas': value}, index=index)
            except:
                print('Não foi possível atualizar o número de replicas para o índice {}'.format(index))
                resp = {'acknowledged': False}
        return resp

    def get_max_result_window(self):
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = self.es.indices.get_settings(index=index, name='*max_result_window')
            try:
                max_result_window = resp[index]['settings']['index']['max_result_window']
            except:
                max_result_window = 10000 # Default value
                
        return max_result_window
    
    def set_max_result_window(self, value):
        for index in settings.SEARCHABLE_INDICES.keys():
            try:
                resp = self.es.indices.put_settings(body={'max_result_window': value}, index=index)
            except:
                print('Não foi possível atualizar o <i>max_result_window</i> para o índice {}'.format(index))
                resp = {'acknowledged': False}
        return resp
    
