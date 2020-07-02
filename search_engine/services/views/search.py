import sys
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

import time
import hashlib
import json

from services.models.log_busca import LogBusca
from services.models.document import Document
from .log import log_search_result
from ..elastic import Elastic
from ..features_extractor import FeaturesExtractor
from ..ranking.tf_idf import TF_IDF

from ..features_extractor import TermVectorsFeaturesExtractor

class Search(View):

    def get(self, request):
        start = time.time() # Medindo wall-clock time da requisição completa
        if not request.user.is_authenticated:
            data = {'is_authenticated': False, 'error': False}
            return JsonResponse(data)

        
        # try:
        self.elastic = Elastic()
        self._read_parameters(request)

        # valida o tamanho da consulta
        query_len = len(''.join(self.query.split()))
        if query_len < 2:
            data = {'invalid_query': True}
            return JsonResponse(data)
        

        # Busca os documentos no elastic
        # total_docs, total_pages, documents, response_time = self._search_documents()
        total_docs, total_pages, documents, response_time = Document().search(self.query, self.page)
        
        # Grava o log da consulta
        LogBusca().save(dict(
            id_sessao = self.sid, 
            id_consulta = self.qid,
            id_usuario = self.id_usuario,
            text_consulta = self.query,
            algoritmo = self.algoritmo,
            data_hora = self.data_hora,
            tempo_resposta = response_time,
            documentos = [ i.id for i in sorted(documents, key = lambda x: x.rank_number) ],
            pagina = self.page,
            resultados_por_pagina = self.results_per_page
        ))

        end = time.time()
        wall_time = end - start
        
        data = {
            'is_authenticated': True,
            'error': False,
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
        return JsonResponse(data)
        
        # except Exception as e:
        #     data = {
        #         'is_authenticated': True,
        #         'error': True,
        #         'error_message': str(sys.exc_info())
        #     }

        #     print(sys.exc_info())
        #     return JsonResponse(data)
        
        
        


    def _read_parameters(self, request):
        # url parameters
        self.raw_query = request.GET['query']
        self.page = int(request.GET.get('page', 1))
        self.sid = request.GET['sid']
        self.qid = request.GET.get('qid', '')

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
    
    
    def _search_documents(self):
        start = self.results_per_page * (self.page - 1)
        end = start + self.results_per_page
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=self.index) \
                .source(['fonte', 'titulo', 'conteudo']) \
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

    def _search_documents_NEW(self):
        start = self.results_per_page * (self.page - 1)
        end = start + self.results_per_page
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=self.index) \
                .source(['fonte', 'titulo']) \
                .query('query_string', query=self.query, phrase_slop='2', default_field='conteudo')[0:100] \
                .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False) \
                .extra(explain=True)

        response = elastic_request.execute()

        ranking_features = FeaturesExtractor(['conteudo', 'titulo']).extract(response)
        tf_idf = TF_IDF(response, ranking_features)
        new_ranking = tf_idf.reranking()[start:end]

        total_docs = 100
        total_pages = (total_docs // self.results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, item in enumerate(new_ranking):
            documents.append({
                'id': item['hit'].meta.id,
                'title': item['hit'].titulo, 
                'description': item['hit'].meta.highlight.conteudo[0],
                'rank_number': self.results_per_page * (self.page-1) + (i+1),
                'source': item['hit'].fonte,
                'type': item['hit'].meta.index,
            })
        
        return total_docs, total_pages, documents, response.took

    
    #Para testar testar essa funçao, troque a funçao de busca usada na função get por essa e certifique-se de estar usando indices com os term_vectors indexados
    def _search_documents_BY_TERM_VECTORS(self):
        indices = ["diarios_teste"] #Usar indice com term_vectors indexados
        total_docs = 100

        start = self.results_per_page * (self.page - 1)
        end = start + self.results_per_page
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
                .source(['fonte', 'titulo']) \
                .query('query_string', query=self.query, phrase_slop='2', default_field='conteudo')[0:total_docs] \
                .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False)

        response = elastic_request.execute()

        ranking_features = TermVectorsFeaturesExtractor(['conteudo', 'titulo'], self.query.split(" "), indices = indices).extract(response) #TODO: parser correto da query

        tf_idf = TF_IDF(response, ranking_features)
        new_ranking = tf_idf.reranking()[start:end]

        total_pages = (total_docs // self.results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, item in enumerate(new_ranking):
            documents.append({
                'id': item['hit'].meta.id,
                'title': item['hit'].titulo, 
                'description': item['hit'].meta.highlight.conteudo[0],
                'rank_number': self.results_per_page * (self.page-1) + (i+1),
                'source': item['hit'].fonte,
                'type': item['hit'].meta.index,
            })
        # print(json.dumps(documents,indent="  "))
        
        return total_docs, total_pages, documents, response.took
