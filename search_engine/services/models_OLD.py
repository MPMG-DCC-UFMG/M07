from django.db import models
from services.elastic import Elastic
import pandas as pd


class ElasticModel:

    def __init__(self):
        self.elastic = Elastic()




class LogBuscas(ElasticModel):

    def __init__(self):
        super().__init__()
        self.index_name = 'log_buscas'
    

    def get_log_buscas(self):
        elastic_result = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
        result_list = []
        for item in elastic_result:
            result_list.append(item.to_dict())
        return result_list

        # results_df = pd.DataFrame((d.to_dict() for d in elastic_result))
        # return results_df
    
