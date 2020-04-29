from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import elasticsearch
import elasticsearch_dsl

from elasticsearch import helpers
import time
import json
import hashlib

from .log import log_search_result

config = json.load(open('../config.json'))
ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']

@require_http_methods(["GET"])
def search(request):
    data_hora = str(time.time())
    algoritmo = 'BM25'
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
    log_search_result(es,
                      id_sessao = sid, 
                      id_consulta = qid,
                      id_usuario = id_usuario,
                      text_consulta = query,
                      algoritmo = algoritmo,
                      data_hora = data_hora,
                      tempo_resposta = response.took,
                      documentos = [ i['id'] for i in sorted(documents, key = lambda x: x['rank_number']) ],
                      pagina = page,
                      resultados_por_pagina = results_per_page )
                      
    return JsonResponse(data)