import json
import elasticsearch
import elasticsearch_dsl
import requests
from elasticsearch import helpers
from django.conf import settings

class Elastic:
    def __init__(self):
        super().__init__()
        self.ELASTIC_ADDRESS = settings.ELASTICSEARCH_DSL['default']['hosts']
        self.es = elasticsearch.Elasticsearch([self.ELASTIC_ADDRESS], timeout=120)
        self.dsl = elasticsearch_dsl
        self.helpers = helpers
    
    def get_cur_algo(self):
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = self.es.indices.get_settings(index=index, name='*sim*')
            try:
                sim = resp[index]['settings']['index']['similarity']['my_similarity']['type']
            except:
                sim = "BM25" # Default value
        return sim

    def get_cur_replicas(self):
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = self.es.indices.get_settings(index=index, name='*replicas')
            try:
                num_repl = resp[index]['settings']['index']['number_of_replicas']
            except:
                print('Não foi possível encontrar o número de replicas para o indice {}'.format(index))
        return num_repl
    
    def set_cur_replicas(self, value):
        for index in settings.SEARCHABLE_INDICES.keys():
            try:
                resp = self.es.indices.put_settings(body={'number_of_replicas': value}, index=index)
            except:
                print('Não foi possível atualizar o número de replicas para o indice {}'.format(index))
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
                print('Não foi possível atualizar o <i>max_result_window</i> para o indice {}'.format(index))
        return resp
    
