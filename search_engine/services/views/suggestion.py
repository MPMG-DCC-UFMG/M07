from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..elastic import Elastic

# from elasticsearch import helpers
# import time
import json
# import hashlib

config = json.load(open('../config.json'))
ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']


@require_http_methods(["GET"])
def query_suggestion(request):
    query = request.GET['query']
    request_body = {
        "_source": "text_consulta", 
        "query": {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "text_consulta",
                    "text_consulta._2gram",
                    "text_consulta._3gram"
                ]
            }
        }
    }

    response = Elastic().es.search(body = request_body, index = "log_buscas")
    hits = [ hit['_source']['text_consulta'] for hit in response['hits']['hits']]
    
    get_position = lambda element: element.lower().find(query.lower()) #TODO: Tratar a query para outros casos alem de lower
    hits.sort(key = get_position)
    # Ordena a lista de sugestoes pela ordem em que a string procurada aparece na query
    # TODO: Melhorar forma de se ordenar essa lista: pode-se ordenar pelo numero de queries que aquele termo apareceu ou
    # pela posicao da palavra em que se encontra o termo buscado. Interresante seria combinar a essa ultima com a primeira
    # TODO: Remover elementos repetidos

    suggestions = []
    for i, hit in enumerate(hits):
        suggestions.append({'label': hit, 'value': 'sugestao '+str(i+1), 'rank_number': i+1, 'suggestion_id': i+1})
    
    # print("[services/query_suggestion] Suggestions: " + str(suggestions))
    
    data = {
        'suggestions': suggestions
    }
    print(data)
    return JsonResponse(data)
