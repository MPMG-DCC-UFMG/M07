import json
import elasticsearch
import elasticsearch_dsl
from elasticsearch import helpers
from django.conf import settings

class Elastic:
    def __init__(self):
        super().__init__()
        ELASTIC_ADDRESS = settings.ELASTICSEARCH_DSL['default']['hosts']
        self.es = elasticsearch.Elasticsearch([ELASTIC_ADDRESS], timeout=120)
        self.dsl = elasticsearch_dsl
        self.helpers = helpers
    
