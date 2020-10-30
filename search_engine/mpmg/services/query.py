import time
import hashlib

from django.conf import settings
from .elastic import Elastic
from mpmg.services.models import LogSearch, Document
from mpmg.services.models import WeightedSearchFieldsConfigs, SearchableIndicesConfigs, SearchConfigs

#Classe funciona como uma especie de interface para usar o Models/Document
class Query:
    def __init__(self, raw_query, page, qid, sid, user_id, instances=[], 
                doc_types=[], start_date=None, end_date=None, group='regular'):
        self.start_time = time.time()
        self.raw_query = raw_query
        self.page = page
        self.qid = qid
        self.sid = sid
        self.user_id = user_id

        self.instances = instances
        self.doc_types = doc_types
        self.start_date = start_date
        self.end_date = end_date
        if self.instances == [] or self.instances == None or self.instances == "":
            self.instances = [] 
        if self.doc_types == [] or self.doc_types == None or self.doc_types == "":
            self.doc_types = [] 
        if self.start_date == "":
            self.start_date = None
        if self.end_date == "":
            self.end_date = None

        self.data_hora = int(time.time()*1000)
        self.query = ' '.join([w for w in self.raw_query.split() if len(w) > 1])
        self.group = group
        
        self.algo_configs = Elastic().get_cur_algo(group=self.group)
        self.results_per_page =  SearchConfigs.get_results_per_page()

        self.weighted_fields =  WeightedSearchFieldsConfigs.get_weigted_search_fields()
        self._generate_query_id()

        self.indices = self._get_search_indices()

    def _generate_query_id(self):
        if not self.qid:
            pre_qid = hashlib.sha1()
            pre_qid.update(bytes(str(self.data_hora) + str(self.user_id) + self.query + self.sid, encoding='utf-8'))
            self.qid = pre_qid.hexdigest()

    # def _get_weighted_fields(self):
    #     self.weighted_fields = []
    #     for field in settings.WEIGHTED_FIELDS:
    #         self.weighted_fields.append( field+"^"+str(settings.WEIGHTED_FIELDS[field]) )

    def is_valid(self):
        query_len = len(''.join(self.query.split()))
        if query_len < 2 or len(self.indices)==0:
            return False
        else:
            return True

    def _get_must_queries(self):
        must_queries = [Elastic().dsl.Q('query_string', query=self.query, fields=self.weighted_fields)]
        return must_queries


    def _get_filters_queries(self):
        filters_queries = []
        if self.instances != None and self.instances != []:
            filters_queries.append(
                Elastic().dsl.Q({'terms': {'instancia.keyword': self.instances}})
            )
        if self.start_date != None and self.start_date != "":
            filters_queries.append(
                Elastic().dsl.Q({'range': {'data': {'gte': self.start_date }}})
            )
        if self.end_date != None and self.end_date != "":
            filters_queries.append(
                Elastic().dsl.Q({'range': {'data': {'lte': self.end_date }}})
            )
        return filters_queries

    def execute(self):
        must_queries = self._get_must_queries()
        filter_queries = self._get_filters_queries()
        
        self.total_docs, self.total_pages, self.documents, self.response_time  = Document().custum_search( self.indices,
            must_queries, filter_queries, self.page, self.results_per_page)
    
        self._log()

        return self.total_docs, self.total_pages, self.documents, self.response_time 

    def _get_search_indices(self):
        if len(self.doc_types) > 0:
            indices = SearchableIndicesConfigs.get_searchable_indices(models=self.doc_types, groups=[self.group])
            # print(indices)
            return indices
        else:
            indices = SearchableIndicesConfigs.get_searchable_indices(groups=[self.group])
            # print(indices)
            return indices

    def _log(self):
        data = dict(
            id_sessao = self.sid,
            id_consulta = self.qid,
            id_usuario = self.user_id,
            text_consulta = self.query,
            data_hora = self.data_hora,
            tempo_resposta = self.response_time,
            documentos = [ i['type']+':'+i['id'] for i in sorted(self.documents, key = lambda x: x['rank_number']) ],
            pagina = self.page,
            resultados_por_pagina = self.results_per_page,
            tempo_resposta_total = time.time() - self.start_time,
            indices = self.indices,
            
            algoritmo = self.algo_configs['type'],
            algoritmo_variaveis = str(self.algo_configs),

            campos_ponderados = self.weighted_fields,

            instancias =  self.instances,
            data_inicial = self.start_date,
            data_final = self.end_date

        )
        # print(data)
        LogSearch().save(data)

        





