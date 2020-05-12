from django.test import TestCase
from django.test import Client
from django.urls import reverse

# Create your tests here.

class SearchResultsTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_total_docs_equal_docs(self):
        # Issue a GET request.
        response = self.client.get(reverse('aduna:search'), {'query': 'query', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 0 results.
        self.assertEqual(len(response.context['documents']), response.context['total_docs'])

    def test_query_no_results(self):
        # Issue a GET request.
        response = self.client.get(reverse('aduna:search'), {'query': '', 'page': 1, 'sid': 'sid', 'qid': ''})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 0 results.
        self.assertEqual(len(response.context['documents']), 1)

    




