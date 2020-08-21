import time
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from mpmg.services.models import LogSearch, LogSearchClick
from .elastic import Elastic

# Create your tests here.

def get_any_id(index="diarios"):
    elastic_response = Elastic().es.search(index = index, _source = False,\
            body = {
                "size": 1, 
                "query": {
                    "match_all": {}
                }
            })
    return elastic_response["hits"]["hits"][0]["_id"]

def get_auth_token(client):
    """
    Função que retorna o token utilizado como input para o header Authorization, necessário para
    autenticação via Django Rest Framework. Em nossos requests, o header é capitalizado e recebe
    o prefixo HTTP_ para ser passado nos requests GET e POST, segundo especificação do Django. 
    Para mais informações, ver trecho que fala sobre headers e META keys em: 
    https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META
    """ 
    response = client.post(reverse('mpmg.services:login'), {'username': 'testuser', 'password': '12345'})
    return response.json()['token']


class SearchTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

    def test_query_request_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('mpmg.services:search'), {'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''})
        
        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)


    def test_query_request_login(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:search'), {'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''}, 
                                    HTTP_AUTHORIZATION='Token '+auth_token)
        
        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)
        
        # Response to JSON
        response = response.json()

        # Checa pela resposta de autenticado.
        self.assertIsNotNone(response['query'])

    def test_invalid_query(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:search'), {'query': '', 'page': 1, 'sid': 'sid', 'qid': ''},
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

        # Response to JSON
        response = response.json()

        # Checa que a mensagem de erro é 'invalid_query'.
        self.assertEqual(response['error_type'], 'invalid_query')

    
class DocumentTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

    def test_document_request_logout(self):
        # GET request enquanto logged out.
        document_id = get_any_id()
        response = self.client.get(reverse('mpmg.services:document'), {'doc_type': 'diarios', 'doc_id': document_id, 'sid': '12345'})

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

    def test_document_request_login(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        document_id = get_any_id()
        response = self.client.get(reverse('mpmg.services:document'), {'doc_type': 'diarios', 'doc_id': document_id, 'sid': '12345'},
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por documento retornado.
        self.assertIsNotNone(response['document'])
    

class LoginTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

    def test_invalid_login(self):
        # POST request para logar com senha errada.
        response = self.client.post(reverse('mpmg.services:login'), {'username': 'testuser', 'password': '123'})
    
        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

        # Response to JSON
        response = response.json()

        # Checa por auth_token == None
        self.assertIsNone(response['token'])

    def test_successful_login(self):
        # POST request para logar com senha correta.
        response = self.client.post(reverse('mpmg.services:login'), {'username': 'testuser', 'password': '12345'})
        
        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por auth_token != None
        self.assertIsNotNone(response['token'])

    def test_successful_logout(self):
        # POST request para deslogar
        auth_token = get_auth_token(self.client)
        response = self.client.post(reverse('mpmg.services:logout'), HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == True
        self.assertTrue(response['success'])


class ElasticTests(TestCase):
    def test_elastic_connection(self):
        #testar conexao com elastic
        ping_result = Elastic().es.ping()
        self.assertTrue(ping_result)

    def test_existence_elastic_indices(self):
        #testar se os indices existem
        indices_list = ["diarios", "processos", "log_buscas", "log_clicks"]
        indices_exist = Elastic().es.indices.exists(index=indices_list)
        self.assertTrue(indices_exist)


class LogTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()
        self.log_search = {
                        'id_sessao': 'sid', 
                        'id_consulta': 'test_query',
                        'id_usuario': '',
                        'text_consulta': 'maria',
                        'algoritmo': '',
                        'data_hora': 123,
                        'tempo_resposta': 10,
                        'documentos': ['a','b','c'],
                        'pagina': 1,
                        'resultados_por_pagina': 10
                        }
        self.log_click = {
                        'item_id': 'test_item_id', 
                        'rank_number': 1, 
                        'item_type': 'test_type', 
                        'qid': 'test_query',
                        'page': 1
                        }
        self.log_click_id = get_any_id('log_clicks')
        self.current_time = int(time.time()*1000)

    def test_post_log_search_result_logout(self):
        # POST request enquanto logged out.
        response = self.client.post(reverse('mpmg.services:log_search'), self.log_search)

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

    def test_post_log_search_result_login(self):
        # POST request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.post(reverse('mpmg.services:log_search'), self.log_search,
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()
        
        # Checa por success == True
        self.assertTrue(response['success'])

    def test_post_log_search_result_click_logout(self):
        # POST request enquanto logged out.
        response = self.client.post(reverse('mpmg.services:log_search_click'), self.log_click)

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)
        
    def test_post_log_search_result_click_login(self):
        # POST request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.post(reverse('mpmg.services:log_search_click'), self.log_click,
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()
        
        # Checa por success == True
        self.assertTrue(response['success'])
        
    def test_get_log_search_result_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('mpmg.services:log_search'), {'end_date': self.current_time})

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

    def test_get_log_search_result_login(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:log_search'), {'end_date': self.current_time},
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()
        
        # Checa por resultado não vazio
        self.assertIsNotNone(response['data'])

    def test_get_log_search_result_start_end_dates(self):
        #TODO: End date < Start date
        pass

    def test_get_log_search_result_click_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('mpmg.services:log_search_click'), {'id_consultas': [self.log_click_id]})

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

    def test_get_log_search_result_click_login(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:log_search_click'), {'id_consultas': [self.log_click_id]},
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()
        
        # Checa por resultado não vazio
        self.assertIsNotNone(response['data'])
    
        
class MetricTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save() 
        self.current_time = int(time.time()*1000)

    def test_get_metric_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('mpmg.services:metrics'), {'metrics': ['no_clicks_query', 'no_results_query'], 'end_date': self.current_time})

        # Checa por response 401 Unauthorized.
        self.assertEqual(response.status_code, 401)

    def test_get_metric_login(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:metrics'), {'metrics': ['no_clicks_query', 'no_results_query'], 'end_date': self.current_time},
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_get_metric_no_date_parameters(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        response = self.client.get(reverse('mpmg.services:metrics'), {'metrics': ['no_clicks_query', 'no_results_query']}, 
                                    HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

    def test_get_metric_start_end_dates(self):
        # GET request enquanto logged in.
        auth_token = get_auth_token(self.client)
        print(self.current_time + 1)
        print(self.current_time)
        print(self.current_time + 1 < self.current_time)
        response = self.client.get(reverse('mpmg.services:metrics'), {'metrics': ['no_clicks_query', 'no_results_query'],
                                    'start_date': self.current_time + 1, 'end_date': self.current_time}, HTTP_AUTHORIZATION='Token '+auth_token)

        # Checa por response 400 Bad Request.
        self.assertEqual(response.status_code, 400)

class SuggestionTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save() 
