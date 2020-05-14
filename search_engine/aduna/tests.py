from django.test import TestCase
from django.test import Client
from django.urls import reverse

# Create your tests here.

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
       response = self.client.get(reverse('aduna:document', kwargs={'doc_type': 'diario', 'doc_id': 'Vw6WiHEBmEbG-RbpxnIs'}))

       # Check that the response is 200 OK.
       self.assertEqual(response.status_code, 200)

    


