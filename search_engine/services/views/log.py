import time
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
        id_sessao=request.POST['id_sessao'],
        id_consulta=request.POST['id_consulta'],
        id_usuario=request.POST['id_usuario'],
        text_consulta=request.POST['text_consulta'],
        algoritmo=request.POST['algoritmo'],
        data_hora=request.POST['data_hora'],
        tempo_resposta=request.POST['tempo_resposta'],
        pagina=request.POST['pagina'],
        resultados_por_pagina=request.POST['resultados_por_pagina'],
        documentos=request.POST['documentos']
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
        id_documento=request.POST['item_id'],
        id_consulta=request.POST['qid'],
        posicao=request.POST['rank_number'],
        tipo_documento=request.POST['item_type'],
        pagina=request.POST['page'],
        timestamp=int(time.time() * 1000),
    ))

    if len(response[1]) == 0:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@csrf_exempt
@require_http_methods(["POST"])
def log_query_suggestion(request):
    query = request.POST['query']
    suggestions = []
    for i in range(5):
        suggestions.append({'label': 'sugestão de consulta '+str(i+1),
                            'value': 'sugestão de consulta '+str(i+1), 'rank_number': i+1, 'suggestion_id': i+1})

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
    print('[LOG SUGGESTION CLICK] session_id: {:s}, user_id: {:s}, suggestion_id: {:s}, rank_number: {:s}'.format(
        session_id, user_id, suggestion_id, rank_number))
    data = {}
    return JsonResponse(data)


@require_http_methods(["GET"])
def get_log_buscas(request):
    user_id = request.GET.get('user_id',  None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    page = request.GET.get('page', 1)

    if user_id == None and start_date == None and end_date == None:
        response = "Error: At least one parameter must be given."
        return JsonResponse({"response": response})

    log_list = LogBusca.get_list_filtered(
        user_id=user_id, start_date=start_date, end_date=end_date, page=page)

    response = {
        "data": log_list
    }

    return JsonResponse(response)


@require_http_methods(["GET"])
def get_log_clicks(request):
    id_consultas = request.GET.getlist('id_consultas', None)  # list of id_consulta
    
    log_list = LogSearchClick.get_list_filtered(id_consultas=id_consultas)

    response = {
        "data": log_list
    }

    return JsonResponse(response)
