from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time
import pandas

from ..elastic import Elastic
from services.models.log_busca import LogBusca
from services.models.log_search_click import LogSearchClick


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result(request):
    '''
    Grava o log de uma consulta. Atualmente o log da consulta já está sendo
    gravado junto do método search da API. Mas ele está exposto aqui para o
    caso dessa dinâmica mudar e ser necessário chamar o método explicitamente.
    '''

    response = LogBusca().save(dict(
        id_sessao             = request.POST['id_sessao'],
        id_consulta           = request.POST['id_consulta'],
        id_usuario            = request.POST['id_usuario'],
        text_consulta         = request.POST['text_consulta'],
        algoritmo             = request.POST['algoritmo'],
        data_hora             = request.POST['data_hora'],
        tempo_resposta        = request.POST['tempo_resposta'],
        pagina                = request.POST['pagina'],
        resultados_por_pagina = request.POST['resultados_por_pagina'],
        documentos            = request.POST['documentos']
    ))

    if len(response[1]) == 0:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result_click(request):
    '''
    Grava no log o item do ranking clicado pelo usuário.
    '''

    response = LogSearchClick().save(dict(
        id_documento   = request.POST['item_id'],
        id_consulta    = request.POST['qid'],
        posicao        = request.POST['rank_number'],
        tipo_documento = request.POST['item_type'],
        pagina         = request.POST['page'],
        timestamp      = int(time.time() * 1000),
    ))

    if len(response[1])  == 0:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@require_http_methods(["GET"])
def query_suggestion(request):
    query = request.GET['query']
    suggestions = []
    for i in range(5):
        suggestions.append({'label': 'sugestão de consulta '+str(i+1), 'value': 'sugestão de consulta '+str(i+1), 'rank_number': i+1, 'suggestion_id': i+1})
    
    data = {
        'suggestions': suggestions
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def log_query_suggestion_click(request):
    session_id = request.POST['session_id']
    user_id = request.POST['user_id']
    rank_number = request.POST['rank_number']
    suggestion_id = request.POST['suggestion_id']
    print('[LOG SUGGESTION CLICK] session_id: {:s}, user_id: {:s}, suggestion_id: {:s}, rank_number: {:s}'.format(session_id, user_id, suggestion_id, rank_number))
    data = {}
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def get_log_buscas(request):
    user_id = request.POST.get('user_id',  None)
    start_date = request.POST.get('start_date', None)
    end_date = request.POST.get('end_date', None)

    if user_id == None and start_date == None and end_date == None:
        response = "Error: At least one parameter must be given."
        return JsonResponse({"response": response})

    body = {
        "size": int(Elastic().es.cat.count("log_buscas").split(" ")[2]), # numero de documentos no indice
        "query": {
            "bool" : {
                "must": []
            }
        }
    }
    
    if user_id != None:
        body["query"]["bool"]["must"].append({
            "term": {
                "id_usuario": user_id
            
            }
        })
    
    if start_date != None:
        start_date = int(float(start_date))
        body["query"]["bool"]["must"].append({
            "range": {
                "data_hora": {
                    "gte": start_date
                }
            }
        })

    if end_date != None:
        end_date = float(end_date)
        if end_date - int(end_date) > 0:
            end_date = int(end_date) + 1
        else:
            end_date = int(end_date)
        body["query"]["bool"]["must"].append({
            "range": {
                "data_hora": {
                    "lte": end_date
                }
            }
        })

    elastic_response = Elastic().es.search(index = "log_buscas", body = body)

    data = []
    for hit in elastic_response["hits"]["hits"]:
        d = hit["_source"]
        d["log_buscas_index_id"] = hit["_id"]
        data.append(d)

    metadata = {
        "took" : elastic_response["took"],
        "timed_out": elastic_response["timed_out"],
        "_shards" : elastic_response["_shards"],
        "total": elastic_response["hits"]["total"]
    }
    if user_id != None: metadata["user_id"] = user_id 
    if start_date != None: metadata["start_date"] = start_date 
    if end_date != None: metadata["end_date"] = end_date
    
    response = {
        "data": data,
        "metadata": metadata
    }
    
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(["POST"])
def get_log_clicks(request):
    consultas = request.POST.getlist('consultas', None) #list of id_consulta

    body = {
        "size": int(Elastic().es.cat.count("log_clicks").split(" ")[2]), # numero de documentos no indice
        "query": {
            "terms": {
            "id_consulta.keyword": consultas
            }
        }
    }
    elastic_response = Elastic().es.search(body = body, index = "log_clicks")

    data = []
    for hit in elastic_response['hits']['hits']:
        d = hit["_source"]
        d["log_buscas_index_id"] = hit["_id"]
        data.append(d)
    
    metadata = {
        "took" : elastic_response["took"],
        "timed_out": elastic_response["timed_out"],
        "_shards" : elastic_response["_shards"],
        "total": elastic_response["hits"]["total"]
    }

    response = {
        "data": data,
        "metadata": metadata
    }

    return JsonResponse(response)
