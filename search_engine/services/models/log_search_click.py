from services.models.elastic_model import ElasticModel


class LogSearchClick(ElasticModel):
    index_name = 'log_clicks'

    def __init__(self, **kwargs):
        index_name = LogSearchClick.index_name
        meta_fields = ['id']
        index_fields = [
            'id_documento',
            'id_consulta',
            'posicao',
            'timestamp',
            'tipo_documento',
            'pagina',
        ]
    
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    
    
    @staticmethod
    def get_list_filtered(id_consultas=None, page='all'):
        if id_consultas != None:
            query_param = {
                "terms": {
                    "id_consulta.keyword": id_consultas
                }
            }
        else:
            query_param = None
        
        return LogSearchClick.get_list(query=query_param, page=page)