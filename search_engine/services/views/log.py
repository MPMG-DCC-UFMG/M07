from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time

from ..elastic import Elastic

def log_search_result(elastic, id_sessao, id_consulta, id_usuario, 
    text_consulta, algoritmo, data_hora, tempo_resposta, documentos, pagina,
    resultados_por_pagina):

    indice = "log_buscas"

    doc = {
        'id_sessao': id_sessao,
        'id_consulta': id_consulta,
        'id_usuario': id_usuario,
        'text_consulta': text_consulta,
        'algoritmo': algoritmo,
        'data_hora': data_hora,
        'tempo_resposta': tempo_resposta,
        'pagina': pagina,
        'resultados_por_pagina': resultados_por_pagina,
        'documentos': documentos
    }

    resp = elastic.helpers.bulk(elastic.es, [{
        "_index": indice,
        "_source": doc
    }])

    if len(resp[1]) == 0: # Test if some error was found during indexing
        print("[services/log_search_result] Search log indexed successfully.")
    else:
        print("[services/log_search_result] ERROR: Error while indexing log: " + str(resp))


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result_click(request):
    timestamp = str(time.time())
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
        "timestamp": float(timestamp),
        "tipo_documento": tipo_documento,
        "pagina": int(pagina),
    }

    response = elastic.helpers.bulk(elastic.es, [{
        "_index": indice,
        "_source": doc
    }])

    print("[services/log_search_result_click] Response from bulk API: " + str(response))

    if len(response[1])  == 0: # Test if some error was found during indexing
        print("[services/log_search_result_click] Click log indexed successfully.")
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