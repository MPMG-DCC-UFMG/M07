from services.elastic import Elastic
from services.models.processo import Processo
from services.models.diario import Diario
from django.conf import settings

class Document:
    '''
    Classe que abstrai as diferentes classes (índices) que podem ser
    pesquisadas pela busca.
    Essa classe é responsável por buscar em diferentes índices e retornar
    uma lista de resultados com diferentes instâncias de classes.

    Diferente das demais, esta classe não herda de ElasticModel justamente
    por não representar um único índice, mas sim um conjunto de diferentes
    índices (classes). Ela fica responsável apenas por realizar a busca e 
    retornar os resultados como uma lista de múltiplas classes.
    '''

    def __init__(self, searchable_indices=None):
        self.elastic = Elastic()
        self.results_per_page = 10
        
        if searchable_indices == None:
            searchable_indices = settings.SEARCHABLE_INDICES

        self.searchable_indices = searchable_indices
        self.index_names = list(self.searchable_indices.keys())

    

    def search(self, query, page_number):
        start = self.results_per_page * (page_number - 1)
        end = start + self.results_per_page
        
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_names) \
                .source(['fonte', 'titulo', 'conteudo']) \
                .query('query_string', query=query, phrase_slop='2', default_field='conteudo')[start:end] \
                .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False, type="unified")

        response = elastic_request.execute()
        total_docs = response.hits.total.value
        total_pages = (total_docs // self.results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, item in enumerate(response):
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            dict_data['description'] = item.meta.highlight.conteudo[0]
            dict_data['rank_number'] = self.results_per_page * (page_number-1) + (i+1)
            dict_data['type'] = item.meta.index

            result_class = self.searchable_indices[item.meta.index]
            documents.append(result_class(**dict_data))
        
        return total_docs, total_pages, documents, response.took


    def search_with_filters(self, query, page_number, instances, doc_types, start_date, end_date):
        start = self.results_per_page * (page_number - 1)
        end = start + self.results_per_page
    
        indices = self.index_names
        if doc_types != None and doc_types != []:
            indices = doc_types

        must = [self.elastic.dsl.Q('query_string', query=query, default_field='conteudo')]
        
        filters = []
        if instances != None and instances != []:
            filters.append(
                self.elastic.dsl.Q({'terms': {'instancia.keyword': instances}})
            )
        if start_date != None and start_date != "":
            filters.append(
                self.elastic.dsl.Q({'range': {'data': {'gte': start_date }}})
            )
        if end_date != None and end_date != "":
            filters.append(
                self.elastic.dsl.Q({'range': {'data': {'lte': end_date }}})
            )
        

        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
                        .source(['fonte', 'titulo', 'conteudo']) \
                        .query("bool", must = must, filter = filters)[start:end] \
                        .highlight('conteudo', fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False, type="unified")                        

        response = elastic_request.execute()
        total_docs = response.hits.total.value
        total_pages = (total_docs // self.results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, item in enumerate(response):
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            dict_data['description'] = item.meta.highlight.conteudo[0]
            dict_data['rank_number'] = self.results_per_page * (page_number-1) + (i+1)
            dict_data['type'] = item.meta.index

            result_class = self.searchable_indices[item.meta.index]
            documents.append(result_class(**dict_data))
        
        return total_docs, total_pages, documents, response.took