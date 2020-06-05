from django.test import TestCase
from django.test import Client
from django.urls import reverse

from elasticsearch import Elasticsearch

# Create your tests here.

def get_any_id():
    elastic_response = Elasticsearch().search(index = "diarios", _source = False,\
            body = {
                "size": 1, 
                "query": {
                    "match_all": {}
                }
            })
    return elastic_response["hits"]["hits"][0]["_id"]

class IndexTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_request(self):
       # Issue a GET request.
       response = self.client.get(reverse('aduna:index'))

       # Check that the response is 200 OK.
       self.assertEqual(response.status_code, 200)

    def test_generate_session_id(self):
       # Issue a GET request.
       response = self.client.get(reverse('aduna:index'))

       # Check that we have a session id.
       self.assertTrue(response.context['sid'])

class SearchTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_request(self):
        # Issue a GET request.
        response = self.client.get(reverse('aduna:search'), {'query': 'maria', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_query_no_results(self):
        # Issue a GET request.
        response = self.client.get(reverse('aduna:search'), {'query': '', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 0 results.
        self.assertEqual(len(response.context['documents']), 0)

    
class DocumentTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_request(self):
       # Issue a GET request.

        document_id = get_any_id()
        response = self.client.get(reverse('aduna:document', kwargs={'doc_type': 'diario', 'doc_id': document_id}))

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    

class LoginTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_request(self):
       # Issue a GET request.
       response = self.client.get(reverse('aduna:login'))

       # Check that the response is 200 OK.
       self.assertEqual(response.status_code, 200)
