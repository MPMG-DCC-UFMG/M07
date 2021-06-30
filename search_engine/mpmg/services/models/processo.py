from mpmg.services.models.elastic_model import ElasticModel


class Processo(ElasticModel):
    index_name = 'processos'

    def __init__(self, **kwargs):
        index_name = Processo.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type', 'score']
        index_fields = [
            'titulo',
            'data',
            'conteudo',
            'fonte',
            'tipo_documento',
            'sentences_vectors'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    