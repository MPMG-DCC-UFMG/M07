from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..elastic import Elastic

import json
import pandas as pd

config = json.load(open('../config.json'))
ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']


def elastic_sugester(query):
    request_body = {
        "_source": "text_consulta",
        "size": int(Elastic().es.cat.count("log_buscas").split(" ")[2]),
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

    elastic_response = Elastic().es.search(body = request_body, index = "log_buscas")
    hits = [ hit['_source']['text_consulta'] for hit in elastic_response['hits']['hits']]
    
    search_result = {
        "hits": hits,
        "total": elastic_response["hits"]["total"]["value"]
    }

    return search_result

def get_word_postion(element, query):
    for i,word in enumerate(element.split(" ")):
        if word.find(query)>=0:
            return i
    return -1

@require_http_methods(["GET"])
def query_suggestion(request):
    query = request.GET['query']

    search_response = elastic_sugester(query)
    processed_suggestions = []
    if search_response["total"]>0:
        suggestions = pd.Series(search_response["hits"], name = "text_consulta").str.replace("\"", "").to_list() 
        df = pd.DataFrame( {"text_consulta": suggestions})
        df = pd.Series(df.groupby(['text_consulta'])['text_consulta'].agg('count'))

        counts = df.to_list()
        suggestions = list(df.index)
        positions = [ get_word_postion(element, query) for element in suggestions]
        df = pd.DataFrame({"suggestions": suggestions, "count": counts, "position": positions})

        df = df.sort_values(['position', 'count'], ascending=[True, False])
        
        processed_suggestions = df.suggestions.to_list()
    
    data = {
        'suggestions': []
    }
    for i, hit in enumerate(processed_suggestions):
        data["suggestions"].append({'label': hit, 'value': hit, 'rank_number': i+1, 'suggestion_id': i+1})
    
    return JsonResponse(data)