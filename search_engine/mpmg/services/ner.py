import subprocess
import json

from django.conf import settings
from mpmg.services. models import SearchableIndicesConfigs

class NER:
    ner_args = ['java', '-cp', 'mp-ufmg-ner.jar:lib/*', 'Pipeline', '-str'] 
    ner_dir = settings.NER_DIR
            
    def execute(cls, query):
        args = cls.ner_args + [query]
        out, err = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cls.ner_dir).communicate()
        ner_data = json.loads(out.decode('utf-8'))

        entities = {}
        for line in ner_data['entities']:
            field = SearchableIndicesConfigs.entity_to_field_map[line['label']]
            if field not in entities:
                entities[field] = set()
            entities[field].add(line['entity'])
        
        for field in entities:
            entities[field] = list(entities[field])
        
        return entities


