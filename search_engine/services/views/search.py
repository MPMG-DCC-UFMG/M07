from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time
import hashlib

from .log import log_search_result
from ..elastic import Elastic

@require_http_methods(["GET"])
def search(request):
    if not request.user.is_authenticated:
        data = {'is_authenticated': False}
        return JsonResponse(data)

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

    elastic = Elastic()

    start = results_per_page * (page - 1)
    end = start + results_per_page
    elastic_request = elastic.dsl.Search(using=elastic.es, index='diarios') \
            .source(['fonte', 'titulo']) \
            .query('query_string', query=query, phrase_slop='2', default_field='conteudo')[start:end] \
            .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False)

    response = elastic_request.execute()
    total_pages = (response.hits.total.value // results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
    documents = []

    for i, hit in enumerate(response):
        documents.append({
            'id': hit.meta.id,
            'title': hit.titulo, 
            'description': hit.meta.highlight.conteudo[0],
            'rank_number': results_per_page * (page-1) + (i+1),
            'source': hit.fonte,
            'type': 'diario',
        })
    
    data = {
        'is_authenticated': True,
        'query': query,
        'total_docs': response.hits.total.value,
        'results_per_page': results_per_page,
        'documents': documents,
        'current_page': page,
        'total_pages': total_pages,
        'qid': qid,
    }

    # Chama funcao para fazer o log da consulta
    log_search_result(elastic,
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