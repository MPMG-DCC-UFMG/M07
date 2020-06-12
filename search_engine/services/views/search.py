import sys
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time
import hashlib

from .log import log_search_result
from ..elastic import Elastic


class Search(View):

    def get(self, request):
        if not request.user.is_authenticated:
            data = {'is_authenticated': False, 'error': False}
            return JsonResponse(data)

        
        try:
            self.elastic = Elastic()
            self._read_parameters(request)

            # valida o tamanho da consulta
            query_len = len(''.join(self.query.split()))
            if query_len < 2:
                data = {'invalid_query': True}
                return JsonResponse(data)
            

            # Busca os documentos no elastic
            total_docs, total_pages, documents, response_time = self._search_documents()
            
            # Grava o log da consulta
            log_search_result(id_sessao = self.sid, 
                id_consulta = self.qid,
                id_usuario = self.id_usuario,
                text_consulta = self.query,
                algoritmo = self.algoritmo,
                data_hora = self.data_hora,
                tempo_resposta = response_time,
                documentos = [ i['id'] for i in sorted(documents, key = lambda x: x['rank_number']) ],
                pagina = self.page,
                resultados_por_pagina = self.results_per_page )

            data = {
                'is_authenticated': True,
                'error': False,
                'query': self.query,
                'total_docs': total_docs,
                'results_per_page': self.results_per_page,
                'documents': documents,
                'current_page': self.page,
                'total_pages': total_pages,
                'qid': self.qid,
            }               
            return JsonResponse(data)
        
        except Exception as e:
            data = {
                'is_authenticated': True,
                'error': True,
                'error_message': str(sys.exc_info())
            }

            print(sys.exc_info())
            return JsonResponse(data)
        
        
        


    def _read_parameters(self, request):
        # url parameters
        self.raw_query = request.GET['query']
        self.page = int(request.GET.get('page', 1))
        self.sid = request.GET['sid']
        self.qid = request.GET.get('qid', '')

        # internal parameters
        self.data_hora = str(time.time())
        self.algoritmo = 'BM25'
        self.results_per_page = 10
        self.id_usuario = request.user.id
        self.index = request.GET.getlist('index', ['diarios', 'processos'])

        self.query = ' '.join([w for w in self.raw_query.split() if len(w) > 1])
        self._generate_query_id()
    

    def _generate_query_id(self):
        if not self.qid:
            pre_qid = hashlib.sha1()
            pre_qid.update(bytes(self.data_hora + str(self.id_usuario) + self.query + self.sid, encoding='utf-8'))
            self.qid = pre_qid.hexdigest()
    
    
    def _search_documents(self):
        start = self.results_per_page * (self.page - 1)
        end = start + self.results_per_page
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=self.index) \
                .source(['fonte', 'titulo']) \
                .query('query_string', query=self.query, phrase_slop='2', default_field='conteudo')[start:end] \
                .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False)

        response = elastic_request.execute()
        total_docs = response.hits.total.value
        total_pages = (total_docs // self.results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, hit in enumerate(response):
            documents.append({
                'id': hit.meta.id,
                'title': hit.titulo, 
                'description': hit.meta.highlight.conteudo[0],
                'rank_number': self.results_per_page * (self.page-1) + (i+1),
                'source': hit.fonte,
                'type': hit.meta.index,
            })
        
        return total_docs, total_pages, documents, response.took
