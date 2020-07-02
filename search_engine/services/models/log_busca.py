from services.models.elastic_model import ElasticModel


class LogBusca(ElasticModel):
    index_name = 'log_buscas'

    def __init__(self, **kwargs):
        index_name = LogBusca.index_name
        meta_fields = ['id']
        index_fields = [
            'id_sessao', 
            'id_consulta', 
            'id_usuario', 
            'text_consulta',
            'algoritmo',
            'data_hora',
            'tempo_resposta',
            'pagina',
            'resultados_por_pagina',
            'documentos'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    