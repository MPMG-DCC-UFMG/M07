from mpmg.services.models.elastic_model import ElasticModel


class DiarioEntidade(ElasticModel):
    index_name = 'diarios_entidades'

    def __init__(self, **kwargs):
        index_name = DiarioEntidade.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type']
        index_fields = [
            'titulo',
            'data',
            'conteudo',
            'fonte',
            'tipo_documento',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
