from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time

from ..elastic import Elastic

def log_search_result(elastic, id_sessao, id_consulta, id_usuario, text_consulta, algoritmo, data_hora,
                      tempo_resposta, documentos, pagina, resultados_por_pagina):
    """
    Stores the query log in the given elasticsearch instace`s index with a give document type.
    """
    indice = "log_buscas"
    doc_type = "log_busca"

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
        "_type": doc_type,
        "_source": doc
    }])

    # Test if some error was found during indexing
    if len(resp[1]) == 0:
        print("[services/log_search_result] Search log indexed successfully.")
    else:
        print("[services/log_search_result] ERROR: Error while indexing log: " + str(resp))


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result_click(request):
    """
    Log the clicks by updating the clicked documents in the log_busca_clicks index via elastic`s update_by_query API.
    Exemple requisition: requests.post("http://localhost:8000/services/log_search_result_click", {'user_id': '31415', 'document_id': '', 'query': '' })
    """
    
    timestamp = str(time.time())
    id_documento = request.POST['item_id']
    posicao = request.POST['rank_number']
    tipo_documento = request.POST['item_type']
    id_consulta = request.POST['qid']
    pagina = request.POST['page']
    
    indice = "log_clicks"
    doc_type = "log_click"

    elastic = Elastic()

    doc = {
        "id_documento": id_documento,
        "id_consulta": id_consulta,
        "posicao": posicao,
        "timestamp": timestamp,
        "tipo_documento": tipo_documento,
        "pagina": pagina,

    }

    response = elastic.helpers.bulk(elastic.es, [{
        "_index": indice,
        "_type": doc_type,
        "_source": doc
    }])

    print("[services/log_search_result_click] Response from bulk API: " + str(response))

    # Test if some error was found during indexing
    if len(response[1])  == 0:
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