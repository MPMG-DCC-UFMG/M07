# from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import lorem


# @csrf_exempt
@require_http_methods(["GET"])
def search(request):
    query = request.GET['query']
    page = request.GET.get('page', 1)

    documents = []
    for i in range(10):
        documents.append({
            'id': i,
            'title': lorem.sentence(), 
            'description': lorem.paragraph(),
            'type': 'diario'
        })
    data = {
        'query': query,
        'total_docs': i+1,
        'total_pages': 10,
        'documents': documents
    }
    return JsonResponse(data)


# @csrf_exempt
@require_http_methods(["GET"])
def document(request):
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']

    document = {
        'id': doc_id,
        'title': lorem.sentence(), 
        'description': lorem.paragraph(),
        'text': lorem.text(),
        'type': 'diario',
    }

    data = {
        'document': document
    }
    return JsonResponse(data)