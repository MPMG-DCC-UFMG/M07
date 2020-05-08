import json
import elasticsearch
import elasticsearch_dsl
from elasticsearch import helpers

class Elastic:
    def __init__(self):
        super().__init__()
        config = json.load(open('../config.json'))
        ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']
        self.es = elasticsearch.Elasticsearch([ELASTIC_ADDRESS], timeout=60)
        self.dsl = elasticsearch_dsl
        self.helpers = helpers
    
