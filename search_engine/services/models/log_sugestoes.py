from services.models.elastic_model import ElasticModel


class LogSugestoes(ElasticModel):
    index_name = 'log_sugestoes'

    def __init__(self, **kwargs):
        index_name = LogSugestoes.index_name
        meta_fields = ['id']
        index_fields = [
            'sugestao',
            'posicao',
            'timestamp',
        ]
    
        super().__init__(index_name, meta_fields, index_fields, **kwargs)


    @staticmethod
    def get_suggestions(query):
        request_body = {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "sugestao",
                    "sugestao._2gram",
                    "sugestao._3gram"
                ]
            }
        }
        response = LogSugestoes.get_list(query=request_body, page='all')
        total = response[0]
        suggestions = [ hit['sugestao'] for hit in response[1]]
        return total, suggestions