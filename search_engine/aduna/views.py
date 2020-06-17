from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import requests
import re


def index(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    # if not request.session.session_key:
    #     request.session.create()
    
    context = {
        'user_name': request.session.get('user_info')['first_name'],
        'sid': request.session.session_key,
        'services_url': settings.SERVICES_URL,
    }
    return render(request, 'aduna/index.html', context)


def search(request):
    if request.GET.get('invalid_query', False) or not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    cookies = {'sessionid': request.session.get('auth_token')}

    query = request.GET['query']
    sid = request.GET['sid']
    qid = request.GET.get('qid', '')
    page = int(request.GET.get('page', 1))

    
    service_response = requests.get(settings.SERVICES_URL+'search', {'query': query, 'page': page, 'sid': sid, 'qid': qid}, cookies=cookies).json()
    
    if service_response['error']:
        messages.add_message(request, messages.ERROR, service_response['error_message'], extra_tags='danger')
        return redirect('/aduna/erro')

    elif service_response['is_authenticated']:
        time_seconds = service_response['time'] / 1000
        context = {
            'user_name': request.session.get('user_info')['first_name'],
            'services_url': settings.SERVICES_URL,
            'query': query,
            'page': page,
            'sid': sid,
            'time': time_seconds,
            'qid': service_response['qid'],
            'total_docs': service_response['total_docs'],
            'results_per_page': range(service_response['results_per_page']),
            'documents': service_response['documents'],
            'total_pages': service_response['total_pages'],
            'results_pagination_bar': range(min(9, service_response['total_pages'])), # Typically show 9 pages. Odd number used so we can center the current one and show 4 in each side. Show less if not enough pages
        }
        
        return render(request, 'aduna/search.html', context)
    else:
        request.session['auth_token'] = None
        return redirect('/aduna/login')
    

def document(request, doc_type, doc_id):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    cookies = {'sessionid': request.session.get('auth_token')}

    service_response = requests.get(settings.SERVICES_URL+'document', {'doc_type': doc_type, 'doc_id':doc_id}, cookies=cookies).json()
    
    if service_response['is_authenticated']:
        document = service_response['document']
        document['text'] = document['text'].replace('\n', '<br>')
        document['text'] = re.sub('(<br>){3,}', '<br>', document['text'])
        context = {
            'user_name': request.session.get('user_info')['first_name'],
            'document': document
        }
        return render(request, 'aduna/document.html', context)
    else:
        request.session['auth_token'] = None
        return redirect('/aduna/login')


def login(request):
    if request.method == 'GET':

        if request.session.get('auth_token'):
            return redirect('/aduna/')
        return render(request, 'aduna/login.html')

    elif request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        service_response = requests.post(settings.SERVICES_URL+'login', {'username': username, 'password': password}).json()
        if service_response['success']:
            request.session['user_info'] = service_response['user_info']
            request.session['auth_token'] = service_response['auth_token']
            return redirect('/aduna/')
        else:
            messages.add_message(request, messages.ERROR, service_response['message'], extra_tags='danger')
            return redirect('/aduna/login')


def logout(request):
    if not request.session.get('auth_token'):
        return redirect('/aduna/login')
    
    cookies = {'sessionid': request.session.get('auth_token')}
    
    service_response = requests.post(settings.SERVICES_URL+'logout', {}, cookies=cookies).json()

    if service_response['success']:
        print(service_response['message'])
        messages.add_message(request, messages.INFO, service_response['message'], extra_tags='info')
        request.session['user_info'] = None
        request.session['auth_token'] = None
        return redirect('/aduna/login')

def erro(request):
    return render(request, 'aduna/erro.html')    