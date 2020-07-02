from services.elastic import Elastic


class ElasticModel(dict):
    '''
    Classe abstrata que representa um índice no elasticsearch.
    Cada índice do elasticsearch deve ter uma classe correspondente 
    que herda dessa.

    Exemplo:

    class MeuIndice(ElasticModel):
        index_name = 'meu_indice'

        def __init__(self, **kwargs):
            index_name = MeuIndice.index_name
            meta_fields = ['_id']
            index_fields = ['campo_um', 'campo_dois']
            super().__init__(index_name, meta_fields, index_fields, **kwargs)
    
    
    Nota: Esta classe herda de dict para que o django consiga serializa-la em
    json automaticamente.
    '''

    # atributos estáticos necessários para os métodos estáticos abaixo
    elastic = Elastic()
    index_name = None
    
    def __init__(self, index_name, meta_fields, index_fields, **kwargs):
        self.elastic = ElasticModel.elastic
        self.index_name = index_name
        self.meta_fields = meta_fields
        self.index_fields = index_fields
        self.allowed_attributes = self.meta_fields + self.index_fields

        for field in self.meta_fields:
            setattr(self, field, kwargs.get(field, None))

        for field in self.index_fields:
            setattr(self, field, kwargs.get(field, None))
        
        serializable_attributes = self.__dict__
        del serializable_attributes['elastic']
        super().__init__(serializable_attributes)
    

    def set_attributes(self, dict_data):
        '''
        Seta os atributos do objeto no formato de dict, onde a chave representa o atributo.
        As chaves do dict_data devem coincidir com as que foram especificadas em index_fields
        e meta_fields
        '''
        for field, value in dict_data.items():
            if field in self.allowed_attributes:
                setattr(self, field, value)


    def save(self, dict_data=None):
        '''
        Salva o objeto no índice. Os valores a serem salvos podem ser passados em dict_data.
        Chaves passadas em dict_data que não estiverem especificadas em index_fields serão ignoradas.
        Se dict_data for igual a None, os atributos do objeto é que serão salvos.
        '''
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')
        
        response = self.elastic.helpers.bulk(Elastic().es, [{
            "_index": self.index_name,
            "_source": dict_data,
        }])
        
        return response
    

    @classmethod
    def get(cls, doc_id):
        '''
        Busca um registro no índice diretamente pelo seu ID.
        Retorna uma instância da classe correspondente ao índice em questão.
        '''

        retrieved_doc = cls.elastic.dsl.Document.get(doc_id, using=cls.elastic.es, index=cls.index_name)
        document = dict({'_id': retrieved_doc.meta.id}, **retrieved_doc.to_dict())
        return cls(**document)
    

    @classmethod
    def get_list(cls, sort=None, query=None):
        '''
        Busca uma lista de documentos do índice. Cada item da lista é uma instância da classe
        em questão. É possível passar parâmetros de ordenação em sort, e também parâmetros de 
        consulta em query.
        Exemplo de sort e de query:

        sort_param = {'data_hora':{'order':'desc'}}
        query_param = {"bool":{"must":{"term":{"text_consulta":"glater"}}}}
        LogBusca.getList(sort=sort_param, query=query_param)
        '''

        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.index_name)
        
        if sort != None:
            search_obj = search_obj.sort(sort)
        
        if query != None:
            search_obj = search_obj.query(cls.elastic.dsl.Q(query))
        
        elastic_result = search_obj.execute()
        
        result_list = []
        for item in elastic_result:
            result_list.append(cls(**dict({'_id': item.meta.id}, **item.to_dict())))
        return result_list