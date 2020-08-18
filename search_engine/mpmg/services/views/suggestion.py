from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from mpmg.services.models import LogSearch

import json
import pandas as pd

def get_word_postion(element, query):
    for i,word in enumerate(element.split(" ")):
        if word.find(query)>=0:
            return i
    return -1

@require_http_methods(["GET"])
def query_suggestion(request):
    query = request.GET['query']

    total, search_response = LogSearch.get_suggestions(query)
    processed_suggestions = []
    if total>0:
        suggestions = pd.Series(search_response, name = "text_consulta").str.replace("\"", "").to_list() 
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