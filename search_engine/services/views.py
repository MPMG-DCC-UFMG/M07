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
    results_per_page = 10
    query = request.GET['query']
    page = int(request.GET.get('page', 1))
    es = elasticsearch.Elasticsearch(['http://localhost:9200/'])
    from_index = results_per_page*(page - 1)
    to_index = results_per_page*page
    request = elasticsearch_dsl.Search(using=es, index='diarios').query('match', conteudo=query)[from_index:to_index]
    response = request.execute()
    documents = []
    for i, hit in enumerate(response):
        documents.append({
            'id': hit.meta.id,
            'title': 'placeholder title', 
            'description': hit.conteudo[:500],
            'rank_number': results_per_page * (page-1) + (i+1),
            'source': hit.fonte,
            'type': 'diario'
        })
    data = {
        'query': query,
        'total_docs': response.hits.total.value,
        'results_per_page': results_per_page,
        'documents': documents,
        'current_page': page,
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
    session_id = request.POST['session_id']
    user_id = request.POST['user_id']
    item_id = request.POST['item_id']
    item_type = request.POST['item_type']
    rank_number = request.POST['rank_number']
    query = request.POST['query']
    print('[LOG RESULT CLICK] query: {:s}, session_id: {:s}, user_id: {:s}, item_id: {:s}, item_type: {:s}, rank_number: {:s}'.format(query, session_id, user_id, item_id, item_type, rank_number))
    data = {}
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