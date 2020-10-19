import sys
import time
import hashlib
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from mpmg.services.models import LogSearch, Document
from ..elastic import Elastic
from ..features_extractor import FeaturesExtractor
from ..ranking.tf_idf import TF_IDF
from ..features_extractor import TermVectorsFeaturesExtractor
from mpmg.services.query import Query


class CompareView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start = time.time() # Medindo wall-clock time da requisição completa

        try:
            self._generate_queries(request)

            if not self.regular_query.is_valid() or not self.replica_query.is_valid():
                data = {'error_type': 'invalid_query'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                
            # Busca os documentos no elastic com Algoritmo 1
            total_docs, total_pages, documents, response_time = self.regular_query.execute()

            # Busca os documentos no elastic com Algoritmo 2 (nos índices replica)
            total_docs_repl, total_pages_repl, documents_repl, response_time_repl = self.replica_query.execute()

            end = time.time()
            wall_time = end - start
            
            data = {
                'query': self.regular_query.query,
                'total_docs': total_docs,
                'time': wall_time,
                'response_time': response_time,
                'results_per_page': self.regular_query.results_per_page,
                'documents': documents,
                'current_page': self.regular_query.page,
                'total_pages': total_pages,
                'qid': self.regular_query.qid, #sera retornado o qid de somente uma consulta
                'start_date': self.regular_query.start_date, 
                'end_date': self.regular_query.end_date,
                'instances': self.regular_query.instances,
                'doc_types': self.regular_query.doc_types,
                'total_docs_repl': total_docs_repl,
                'total_pages_repl': total_pages_repl,
                'documents_repl': documents_repl,
                'response_time_repl': response_time_repl,
                'algorithm_base': self.regular_query.algo_configs['type'],#TODO: acertar isso para passar como parametro o grupo
                'algorithm_repl': self.replica_query.algo_configs['type'],#TODO: acertar isso para passar como parametro o grupo
            }               
            return Response(data)
        
        except Exception as e:
            data = {
                'error_message': str(sys.exc_info())
            }
            print(sys.exc_info())
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_queries(self, request):
        # url parameters
        raw_query = request.GET['query']
        page = int(request.GET.get('page', 1))
        sid = request.GET['sid']
        qid = request.GET.get('qid', '')
        instances = request.GET.getlist('instances', [])
        doc_types = request.GET.getlist('doc_types', [])
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        user_id = request.user.id

        self.regular_query = Query(raw_query, page, qid, sid, user_id, instances, 
                doc_types, start_date, end_date)

        self.replica_query = Query(raw_query, page, qid, sid, user_id, instances, 
                doc_types, start_date, end_date, group='replica') #Modificar o doc_types para incluir os indices do outro alg
        