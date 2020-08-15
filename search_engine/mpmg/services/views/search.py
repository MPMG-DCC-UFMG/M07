import sys
import time
import hashlib
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from mpmg.services.models.log_busca import LogBusca
from mpmg.services.models.document import Document
from .log import log_search_result
from ..elastic import Elastic
from ..features_extractor import FeaturesExtractor
from ..ranking.tf_idf import TF_IDF
from ..features_extractor import TermVectorsFeaturesExtractor


class Search(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start = time.time() # Medindo wall-clock time da requisição completa

        try:
            self.elastic = Elastic()
            self._read_parameters(request)

            # valida o tamanho da consulta
            query_len = len(''.join(self.query.split()))
            if query_len < 2:
                data = {'error_type': 'invalid_query'}
                return Response(data, status=400) # bad request status code
                
            # Busca os documentos no elastic
            total_docs, total_pages, documents, response_time = Document().search_with_filters(
                self.query, self.page, self.instances, self.doc_types, self.start_date, self.end_date)

            # Grava o log da consulta
            LogBusca().save(dict(
                id_sessao = self.sid, 
                id_consulta = self.qid,
                id_usuario = self.id_usuario,
                text_consulta = self.query,
                algoritmo = self.algoritmo,
                data_hora = self.data_hora,
                tempo_resposta = response_time,
                documentos = [ i['id'] for i in sorted(documents, key = lambda x: x['rank_number']) ],
                pagina = self.page,
                resultados_por_pagina = self.results_per_page,
                tempo_resposta_total = time.time() - start,
                indices = self.doc_types,
                instancias =  self.instances,
                data_inicial = self.start_date,
                data_final = self.end_date
            ))

            end = time.time()
            wall_time = end - start
            
            data = {
                'query': self.query,
                'total_docs': total_docs,
                'time': wall_time,
                'time_elastic': response_time,
                'results_per_page': self.results_per_page,
                'documents': documents,
                'current_page': self.page,
                'total_pages': total_pages,
                'qid': self.qid,
            }               
            return Response(data)
        
        except Exception as e:
            data = {
                'error_message': str(sys.exc_info())
            }
            print(sys.exc_info())
            return Response(data, status=500)
        
        
    def _read_parameters(self, request):
        # url parameters
        self.raw_query = request.GET['query']
        self.page = int(request.GET.get('page', 1))
        self.sid = request.GET['sid']
        self.qid = request.GET.get('qid', '')
        self.instances = request.GET.getlist('instances', [])
        self.doc_types = request.GET.getlist('doc_types', [])
        self.start_date = request.GET.get('start_date', None)
        self.end_date = request.GET.get('end_date', None)
        if self.start_date == "":
            self.start_date = None
        if self.end_date == "":
            self.end_date = None

        # internal parameters
        self.data_hora = int(time.time()*1000)
        self.algoritmo = 'BM25'
        self.results_per_page = 10
        self.id_usuario = request.user.id
        self.index = request.GET.getlist('index', settings.SEARCHABLE_INDICES.keys())
        self.query = ' '.join([w for w in self.raw_query.split() if len(w) > 1])
        self._generate_query_id()
    

    def _generate_query_id(self):
        if not self.qid:
            pre_qid = hashlib.sha1()
            pre_qid.update(bytes(str(self.data_hora) + str(self.id_usuario) + self.query + self.sid, encoding='utf-8'))
            self.qid = pre_qid.hexdigest()