# from django.shortcuts import render
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

# @csrf_exempt
@require_http_methods(["GET"])
def search(request):
    data_hora = str(time.time())
    results_per_page = 10 #numero magico
    id_usuario = str(31415) #numero magico
    query = request.GET['query']
    page = int(request.GET.get('page', 1))
    sid = request.GET['sid']
    qid = request.GET.get('qid', '')    
    if not qid: # Gera um novo id de consulta
        pre_qid = hashlib.sha1()
        pre_qid.update(bytes(data_hora + id_usuario + query + sid, encoding='utf-8'))
        qid = pre_qid.hexdigest()

    es = elasticsearch.Elasticsearch([ELASTIC_ADDRESS]) # deve ser uma variavel global
    start = results_per_page * (page - 1)
    end = start + results_per_page
    request = elasticsearch_dsl.Search(using=es, index='diarios').query('match',
             conteudo=query)[start:end].highlight('conteudo', fragment_size=500,
             pre_tags='<strong>', post_tags='</strong>')

    response = request.execute()
    total_pages = (response.hits.total.value // results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
    documents = []

    for i, hit in enumerate(response):
        documents.append({
            'id': hit.meta.id,
            'title': 'placeholder title', 
            'description': hit.meta.highlight.conteudo[0],
            'rank_number': results_per_page * (page-1) + (i+1),
            'source': hit.fonte,
            'type': 'diario',
        })
    
    data = {
        'query': query,
        'total_docs': response.hits.total.value,
        'results_per_page': results_per_page,
        'documents': documents,
        'current_page': page,
        'total_pages': total_pages,
        'qid': qid,
    }

    # Chama funcao para fazer o log da consulta
    # TODO: Passar qid (query id) aqui
    log_search_result(es, data, id_usuario , data_hora, response.took )
    
    return JsonResponse(data)

# @csrf_exempt
# @require_http_methods(["POST"])
def log_search_result(es, data , id_usuario, data_hora, tempo_resposta):
    """
    Stores the query log in the given elasticsearch instace`s index called log_busca_click, 
    typing each document as log_busca_clicks.
    """

    # Lamda functions that gerates the actions to be bulked
    generate_bulk = lambda data, id_usuario, data_hora, tempo_resposta: [( yield {
        "_index": "log_busca_clicks",
        "_type": "log_busca_click",
        "_source": {
            'id_usuario': id_usuario,
            'texto_consulta': data['query'],
            'data_hora': data_hora,
            'tempo_resposta': tempo_resposta,
            'id_documento': documento['id'],
            'rank': documento['rank_number'],
            'pagina': data['current_page']
        }
    }) for documento in data['documents']]

    # Bulk the given actions
    resp = helpers.bulk(es, generate_bulk(data, id_usuario, data_hora, tempo_resposta) )
    
    # Test if some error was found during indexing
    if len(resp[1]) > 0:
        print("Error while indexing logs: " + str(resp))



# @csrf_exempt
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
def log_search_result_click(request):
    """
    Log the clicks by updating the clicked documents in the log_busca_clicks index via elastic`s update_by_query API.
    Exemple requisition: requests.post("http://localhost:8000/services/log_search_result_click", {'user_id': '31415', 'document_id': '', 'query': '' })
    """

    click_data_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    id_usuario = request.POST['user_id']
    texto_consulta = request.POST['query']
    id_documento = request.POST['document_id']

    # Creates the request body
    body = {
        "script": {
            "source": "ctx._source.click_hora = params.hora",
            "lang": "painless",
            "params":{
                "hora" : click_data_hora
            }
        },
        "query": {
            "bool": {
                "must": [
                    { "term": {"id_usuario.keyword": id_usuario } },
                    { "term": {"texto_consulta.keyword": texto_consulta } },
                    { "term": {"id_documento.keyword": id_documento } }
                ]
            }
        }
    }
    
    # Calls update_by_query API
    response = {}
    es = elasticsearch.Elasticsearch([ELASTIC_ADDRESS]) # deve ser uma variavel global
    response = es.update_by_query(index="log_busca_clicks", body=body)

    print("[LOG SUGGESTION CLICK] " + str(response))
    return JsonResponse(response)


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