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
        print(self.ELASTIC_ADDRESS)
        for index in settings.SEARCHABLE_INDICES.keys():
            resp = requests.get('http://' + self.ELASTIC_ADDRESS + 
                                '/{}/_settings/*sim*?pretty'.format(index)).json()
            try:
                sim = resp[index]['settings']['index']['similarity']['my_similarity']['type']
            except:
                sim = "BM25"
        return sim
    
