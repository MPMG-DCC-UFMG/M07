import re
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


def index(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    context = {
        'user_name': request.session.get('user_info')['first_name'],
        'services_url': settings.SERVICES_URL,
        'auth_token': request.session.get('auth_token'),
    }
    return render(request, 'aduna/index.html', context)


def search(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    sid = request.session.session_key
    query = request.GET['query']
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    instances = request.GET.getlist('instance', [])
    doc_types = request.GET.getlist('doc_type', [])
    start_date = request.GET.get('start_date', None)
    if start_date == "":
        start_date = None
    end_date = request.GET.get('end_date', None)
    if end_date == "":
        end_date = None
    
    params = {
        'query': query, 
        'page': page, 
        'sid': sid, 
        'qid': qid, 
        'instances': instances, 
        'doc_types': doc_types,
        'start_date': start_date,
        'end_date': end_date
    }
    service_response = requests.get(settings.SERVICES_URL+'search', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')

    else:
        context = {
            'auth_token': request.session.get('auth_token'),
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_docs'],
            'results_per_page': range(response_content['results_per_page']),
            'documents': response_content['documents'],
            'total_pages': response_content['total_pages'],
            'results_pagination_bar': range(min(9, response_content['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'start_date': datetime.strptime(response_content['start_date'], '%Y-%m-%d') if response_content['start_date'] != None else None,
            'end_date': datetime.strptime(response_content['end_date'], '%Y-%m-%d') if response_content['end_date'] != None else None,
            'instances': response_content['instances'],
            'doc_types': response_content['doc_types'],
            'filter_instances': ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2'],
            'filter_doc_types': ['diarios', 'processos']
        }
        
        return render(request, 'aduna/search.html', context)
    

def document(request, doc_type, doc_id):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}
    sid = request.session.session_key
    service_response = requests.get(settings.SERVICES_URL+'document', {'doc_type': doc_type, 'doc_id': doc_id}, headers=headers)

    if service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')
    else:
        response_content = service_response.json()
        document = response_content['document']
        document['conteudo'] = document['conteudo'].replace('\n', '<br>')
        document['conteudo'] = re.sub('(<br>){3,}', '<br>', document['conteudo'])
        context = {
            'user_name': request.session.get('user_info')['first_name'],
            'document': document
        }
        return render(request, 'aduna/document.html', context)


def login(request):
    if request.method == 'GET':
        if request.session.get('auth_token'):
            return redirect('/aduna/')
        return render(request, 'aduna/login.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        service_response = requests.post(settings.SERVICES_URL+'login', {'username': username, 'password': password})
        if service_response.status_code == 401:
            messages.add_message(request, messages.ERROR, 'Usuário ou senha inválidos.', extra_tags='danger')
            return redirect('/aduna/login')
        else:
            response_content = service_response.json()
            request.session['user_info'] = response_content['user_info']
            request.session['auth_token'] = response_content['token']
            return redirect('/aduna/')
            


def logout(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}
    service_response = requests.post(settings.SERVICES_URL+'logout', headers=headers)

    messages.add_message(request, messages.INFO, 'Você saiu.', extra_tags='info')
    request.session['user_info'] = None
    request.session['auth_token'] = None
    return redirect('/aduna/login')

def erro(request):
    return render(request, 'aduna/erro.html')    


def search_comparison(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    headers = {'Authorization': 'Token '+request.session.get('auth_token')}

    sid = request.session.session_key
    query = request.GET['query']
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))
    instances = request.GET.getlist('instance', [])
    doc_types = request.GET.getlist('doc_type', [])
    start_date = request.GET.get('start_date', None)
    if start_date == "":
        start_date = None
    end_date = request.GET.get('end_date', None)
    if end_date == "":
        end_date = None
    
    params = {
        'query': query, 
        'page': page, 
        'sid': sid, 
        'qid': qid, 
        'instances': instances, 
        'doc_types': doc_types,
        'start_date': start_date,
        'end_date': end_date
    }
    service_response = requests.get(settings.SERVICES_URL+'search_comparison', params, headers=headers)
    response_content = service_response.json()

    if service_response.status_code == 500:
        messages.add_message(request, messages.ERROR, response_content['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response.status_code == 401:
        request.session['auth_token'] = None
        request.session['user_info'] = None
        return redirect('/aduna/login')

    else:
        context = {
            'auth_token': request.session.get('auth_token'),
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': response_content['time'],
            'qid': response_content['qid'],
            'total_docs': response_content['total_docs'],
            'results_per_page': range(response_content['results_per_page']),
            'documents': response_content['documents'],
            'total_pages': response_content['total_pages'],
            'results_pagination_bar': range(min(9, response_content['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
            'start_date': datetime.strptime(response_content['start_date'], '%Y-%m-%d') if response_content['start_date'] != None else None,
            'end_date': datetime.strptime(response_content['end_date'], '%Y-%m-%d') if response_content['end_date'] != None else None,
            'instances': response_content['instances'],
            'doc_types': response_content['doc_types'],
            'filter_instances': ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2'],
            'filter_doc_types': ['diarios', 'processos'],
            'total_docs_repl': response_content['total_docs_repl'],
            'total_pages_repl': response_content['total_pages_repl'],
            'documents_repl': response_content['documents_repl'],
            'response_time': response_content['response_time'],
            'response_time_repl': response_content['response_time_repl'],
            'algorithm_base': response_content['algorithm_base'],
            'algorithm_repl': response_content['algorithm_repl'],
        }
        
        return render(request, 'aduna/search_comparison.html', context)