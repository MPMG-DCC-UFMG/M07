from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


# Create your tests here.

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

    def test_query_no_results(self):
        # GET request enquanto logged in.
        user_login(self.client)
        response = self.client.get(reverse('services:search'), {'query': '', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa que o resultado contém 0 resultados.
        self.assertEqual(len(response['documents']), 0)

    
class DocumentTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_document_request_logout(self):
        # GET request enquanto logged out.
        response = self.client.get(reverse('services:document'), {'doc_type': 'diario', 'doc_id': '7OhmUnIBh9Xgt3ZVq2bI'})

        # Checa por response 200 OK.
        self.assertEqual(response.status_code, 200)

        # Response to JSON
        response = response.json()

        # Checa pela resposta de não autenticado.
        self.assertFalse(response['is_authenticated'])

    def test_document_request_login(self):
        # GET request enquanto logged in.
        user_login(self.client)
        response = self.client.get(reverse('services:document'), {'doc_type': 'diario', 'doc_id': '7OhmUnIBh9Xgt3ZVq2bI'})

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
