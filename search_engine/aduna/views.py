from django.shortcuts import render
from django.http import HttpResponse

import requests

SERVICES_URL = 'http://127.0.0.1:8000/services/'

def index(request):
    context = {}
    return render(request, 'aduna/index.html', context)
    # return HttpResponse("Hello, world. You're at the polls index.")


def search(request):
    query = request.GET['query']
    page = request.GET.get('page', 1)
    service_response = requests.get(SERVICES_URL+'search', {'query': query, 'page': page}).json()
    
    context = {
        'query': query, 
        'page': page,
        'total_docs': service_response['total_docs'],
        'total_pages': range(service_response['total_pages']),
        'documents': service_response['documents']
    }
    return render(request, 'aduna/search.html', context)


def document(request, doc_type, doc_id):
    service_response = requests.get(SERVICES_URL+'document', {'doc_type': doc_type, 'doc_id':doc_id}).json()
    document = service_response['document']
    
    context = {'document': document}
    return render(request, 'aduna/document.html', context)