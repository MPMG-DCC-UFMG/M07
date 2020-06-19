from collections import defaultdict

class FeaturesExtractor:
    '''
    Parseia o "explain" do elasticsearch para extrair features.
    Numa pesquisa por "belo horizonte" em documentos com os campos "conteudo" e "titulo",
    produzirá a seguinte estrutura:

        DOC_ID:{
            conteudo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                    termo2:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            },
            titulo:{
                field_length:0, 
                avg_field_length:0,
                matched_terms:{
                    termo1:{tf:0, idf:0, num_docs_term:0, total_docs:0},
                }
            }
        }
    
    field_length: número de tokens daquele campo naquele documento
    avg_field_length: tamanho médio desse campo em todo o índice
    tf: frequeência do termo naquele campo para aquele documento
    idf: inverso da frequência do termo para aquele campo naquele documento
    num_docs_term: número de documentos que contém o termo em questão.
    total_docs: número de documentos que possui o campo em questão
    '''
    def __init__(self, fields):
        self.features = {}
        self.fields = fields
    

    def extract(self, elastic_response):
        for hit in elastic_response:
            # print(hit.meta.id)
            self.features[hit.meta.id] = {}
            for field in self.fields:
                self.features[hit.meta.id][field] = {'matched_terms':defaultdict(dict), 'field_length':0, 'avg_field_length':0}
            
            self._parse_node(hit.meta.id, None, None, hit.meta.explanation, '')
        
        # print(self.features)
        return self.features
    

    def _parse_node(self, doc_id, current_field, current_term, json_node, space):
        # qual campo e qual termo
        if json_node['description'].startswith('weight'):
            current_field = json_node['description'][7:json_node['description'].index(':')]
            current_term = json_node['description'][json_node['description'].index(':')+1:json_node['description'].index(' ')]
            # print(current_field, current_term)
        
        elif json_node['description'].startswith('idf,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['idf'] = json_node['value']
        
        elif json_node['description'].startswith('n,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['num_docs_term'] = json_node['value']
        
        elif json_node['description'].startswith('N,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['total_docs'] = json_node['value']
        
        elif json_node['description'].startswith('tf,'):
            self.features[doc_id][current_field]['matched_terms'][current_term]['tf'] = json_node['value']
        
        elif json_node['description'].startswith('dl,'):
            self.features[doc_id][current_field]['field_length'] = json_node['value']
        
        elif json_node['description'].startswith('avgdl,'):
            self.features[doc_id][current_field]['avg_field_length'] = json_node['value']
        
        # print(space, json_node['value'], json_node['description'])
        if len(json_node['details']) > 0:
            for item in json_node['details']:
                self._parse_node(doc_id, current_field, current_term, item, space+'    ')
