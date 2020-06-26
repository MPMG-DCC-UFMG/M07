from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time
import pandas

from ..elastic import Elastic

def log_search_result( id_sessao, id_consulta, id_usuario, 
    text_consulta, algoritmo, data_hora, tempo_resposta, documentos, pagina,
    resultados_por_pagina):

    indice = "log_buscas"
    doc = {
        'id_sessao': id_sessao,
        'id_consulta': id_consulta,
        'id_usuario': id_usuario,
        'text_consulta': text_consulta,
        'algoritmo': algoritmo,
        'data_hora': round(float(data_hora), 6),
        'tempo_resposta': int(tempo_resposta),
        'pagina': int(pagina),
        'resultados_por_pagina': int(resultados_por_pagina),
        'documentos': documentos
    }

    resp = Elastic().helpers.bulk(Elastic().es, [{
        "_index": indice,
        "_source": doc
    }])

    if len(resp[1]) == 0: # Test if some error was found during indexing
        return {"search_result_logged": True}
    else :
        return {"search_result_logged": False}


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result_click(request):
    timestamp = time.time()
    id_documento = request.POST['item_id']
    posicao = request.POST['rank_number']
    tipo_documento = request.POST['item_type']
    id_consulta = request.POST['qid']
    pagina = request.POST['page']
    
    indice = "log_clicks"

    elastic = Elastic()

    doc = {
        "id_documento": id_documento,
        "id_consulta": id_consulta,
        "posicao": int(posicao),
        "timestamp": round(float(timestamp), 6),
        "tipo_documento": tipo_documento,
        "pagina": int(pagina),
    }

    response = elastic.helpers.bulk(elastic.es, [{
        "_index": indice,
        "_source": doc
    }])

    if len(response[1])  == 0: # Test if some error was found during indexing
        # print("[services/log_search_result_click] Click log indexed successfully.")
        return JsonResponse({"click_logged": True})
    else:
        print("[services/log_search_result_click] ERROR: Error while indexing click log: " + str(response))
        return JsonResponse({"click_logged": False})


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
