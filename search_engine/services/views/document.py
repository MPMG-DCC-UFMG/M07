from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import elasticsearch
import elasticsearch_dsl
# import lorem

from elasticsearch import helpers
import time
import json
import hashlib

config = json.load(open('../config.json'))
ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']


@require_http_methods(["GET"])
def document(request):
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    es = elasticsearch.Elasticsearch([ELASTIC_ADDRESS]) # deve ser uma variavel global
    retrieve_doc = elasticsearch_dsl.Document.get(doc_id, using=es, index='diarios')
    document = {
        'id': doc_id,
        'title': 'placeholder title', 
        'description': 'placeholder description',
        'text': retrieve_doc.conteudo,
        'source': retrieve_doc.fonte,
        'type': 'diario',
    }

    data = {
        'document': document
    }
    return JsonResponse(data)