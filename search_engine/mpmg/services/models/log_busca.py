from mpmg.services.models.elastic_model import ElasticModel


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
            'documentos',
            'tempo_resposta_total',
            'indices',
            'instancias',
            'data_inicial',
            'data_final',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    
    @staticmethod
    def get_list_filtered(id_sessao=None, id_consulta=None, id_usuario=None, text_consulta=None, start_date=None, end_date=None, page='all', sort=None):
        query_param = {
            "bool": {
                "must": []
            }
        }

        if id_usuario:
            query_param["bool"]["must"].append({
                "term": {
                    "id_usuario": id_usuario

                }
            })
        
        if text_consulta:
            query_param["bool"]["must"].append({
                "term": {
                    "text_consulta": text_consulta

                }
            })

        if start_date:
            query_param["bool"]["must"].append({
                "range": {
                    "data_hora": {
                        "gte": start_date
                    }
                }
            })

        if end_date:
            query_param["bool"]["must"].append({
                "range": {
                    "data_hora": {
                        "lte": end_date
                    }
                }
            })

        return LogBusca.get_list(query=query_param, page=page, sort=sort)

    @staticmethod
    def get_suggestions(query):
        request_body = {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "text_consulta",
                    "text_consulta._2gram",
                    "text_consulta._3gram"
                ]
            }
        }
        response = LogBusca.get_list(query=request_body, page='all')
        total = response[0]
        suggestions = [ hit['text_consulta'] for hit in response[1]]
        return total, suggestions