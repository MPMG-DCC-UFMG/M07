from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from .elastic import Elastic

# Create your tests here.

def get_any_id():
    elastic_response = Elastic().es.search(index = "diarios", _source = False,\
            body = {
                "size": 1, 
                "query": {
                    "match_all": {}
                }
            })
    return elastic_response["hits"]["hits"][0]["_id"]

def user_login(client):
    """Faz login no 'client' especificado."""
    client.logout()
    user = User.objects.get_or_create(username='testuser')[0]
    client.force_login(user)

class SearchTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_query_request_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('services:search'), {'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''})
        
        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de não autenticado.
        self.assertFalse(response['is_authenticated'])

    def test_query_request_login(self):
        # GET request enquanto logged in.
        user_login(self.client)
        response = self.client.get(reverse('services:search'), {'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de autenticado.
        self.assertTrue(response['is_authenticated'])

    def test_invalid_query(self):
        # GET request enquanto logged in.
        user_login(self.client)
        response = self.client.get(reverse('services:search'), {'query': '', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa que o resultado contém 0 resultados.
        self.assertTrue(response['invalid_query'])

    
class DocumentTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_document_request_logout(self):
        # GET request enquanto logged out.
        document_id = get_any_id()
        response = self.client.get(reverse('services:document'), {'doc_type': 'diarios', 'doc_id': document_id, 'sid': '12345'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de não autenticado.
        self.assertFalse(response['is_authenticated'])

    def test_document_request_login(self):
        # GET request enquanto logged in.
        user_login(self.client)
        
        document_id = get_any_id()
        response = self.client.get(reverse('services:document'), {'doc_type': 'diarios', 'doc_id': document_id, 'sid': '12345'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de autenticado.
        self.assertTrue(response['is_authenticated'])
    

class LoginTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

    def test_invalid_login(self):
        # POST request para logar com senha errada.
        response = self.client.post(reverse('services:login'), {'username': 'testuser', 'password': '123'})
    
        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == False e auth_token == None
        self.assertFalse(response['success'])
        self.assertIsNone(response['auth_token'])

    def test_succesful_login(self):
        # POST request para logar com senha correta.
        response = self.client.post(reverse('services:login'), {'username': 'testuser', 'password': '12345'})
    
        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa por success == True e auth_token != None
        self.assertTrue(response['success'])
        self.assertIsNotNone(response['auth_token'])

    def test_succesful_logout(self):
        # POST request para logar com senha correta.
        response = self.client.post(reverse('services:login'), {'username': 'testuser', 'password': '12345'})

        # POST request para deslogar
        response = self.client.post(reverse('services:logout'))
    
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


from .views import log_search_result
class LogTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_log_search_result(self):
        log_response = log_search_result(
                        id_sessao = "sid", 
                        id_consulta = "test_query",
                        id_usuario = "",
                        text_consulta = "maria",
                        algoritmo = "",
                        data_hora = 123,
                        tempo_resposta = 10,
                        documentos = ["a","b","c"],
                        pagina = 1,
                        resultados_por_pagina = 10 )

        self.assertTrue(log_response["search_result_logged"])

    def test_log_search_result_click(self):
        log = {

            'item_id': 'test_item_id', 
            'rank_number': 1, 
            'item_type': 'test_type', 
            'qid': 'test_query',
            'page': 1
        }
        response = self.client.post(reverse('services:log_search_result_click'), log)
        self.assertEqual(response.status_code, 200)
        
        response = response.json()
        self.assertTrue(response["click_logged"])
        
        

