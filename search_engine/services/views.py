# from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import elasticsearch
import elasticsearch_dsl
# import lorem


# @csrf_exempt
@require_http_methods(["GET"])
def search(request):
    query = request.GET['query']
    page = request.GET.get('page', 1)
    es = elasticsearch.Elasticsearch(['http://localhost:9200/'])
    request = elasticsearch_dsl.Search(using=es, index='diarios').query('match', conteudo=query)
    response = request.execute()
    documents = []
    for i, hit in enumerate(response):
        documents.append({
            'id': hit.meta.id,
            'title': 'placeholder title', 
            'description': hit.conteudo[:500],
            'type': 'diario'
        })
    data = {
        'query': query,
        'total_docs': response.hits.total.value,
        'total_pages': 10,
        'documents': documents
    }
    return JsonResponse(data)


# @csrf_exempt
@require_http_methods(["GET"])
def document(request):
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    es = elasticsearch.Elasticsearch(['http://localhost:9200/'])
    retrieve_doc = elasticsearch_dsl.Document.get(doc_id, using=es, index='diarios')
    document = {
        'id': doc_id,
        'title': 'placeholder title', 
        'description': 'placeholder description',
        'text': retrieve_doc.conteudo,
        'type': 'diario',
    }

    data = {
        'document': document
    }
    return JsonResponse(data)