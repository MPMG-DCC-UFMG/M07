import sys
import time

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
from ..query import Query

class SearchView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        start = time.time() # Medindo wall-clock time da requisição completa

        # try:
        #     self.elastic = Elastic()
        #     self._generate_query(request)

            # valida o tamanho da consulta
        if self.query.is_valid():
            data = {'error_type': 'invalid_query'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        # Busca os documentos no elastic
        total_docs, total_pages, documents, response_time = self.query.execute()

        end = time.time()
        wall_time = end - start
        
        data = {
            'query': self.query.query,
            'total_docs': total_docs,
            'time': wall_time,
            'time_elastic': response_time,
            'results_per_page': self.query.results_per_page,
            'documents': documents,
            'current_page': self.query.page,
            'total_pages': total_pages,
            'qid': self.query.qid,
            'start_date': self.query.start_date,
            'end_date': self.query.end_date,
            'instances': self.query.instances,
            'doc_types': self.query.doc_types,
        }               
        return Response(data)
        
        # except Exception as e:
        #     data = {
        #         'error_message': str(sys.exc_info())
        #     }
        #     print(sys.exc_info())
        #     return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def _generate_query(self, request):
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

        self.query = Query(raw_query, page, qid, sid, user_id, instances, 
                doc_types, start_date, end_date)



        

    

    