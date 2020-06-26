import pandas as pd
import time
import requests


#TODO: Usar caminhos das requests para o get_log_busca e get_log_clicks pegando os endereços de uma arquivo de config
class Metrics:
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date 
        self.end_date = end_date
        self.query_log, self.click_log = self._get_logs()
        
    def _get_logs(self):
        params = {}
        if self.start_date == None and self.end_date == None:
            raise Exception('At leat one parameter must be given.')
        if self.start_date != None:
            params['start_date'] = self.start_date
        if self.end_date != None:
            params['end_date'] = self.end_date
        
        query_response = requests.post(url = "http://localhost:8000/services/get_log_buscas", data = params).json()
        query_log = pd.DataFrame.from_dict(query_response['data'])
        
        consultas = query_log['id_consulta'].to_list()
        click_response = requests.post("http://localhost:8000/services/get_log_clicks", data = {"consultas": consultas }).json()
        click_log = pd.DataFrame.from_dict(click_response['data'])
        return query_log, click_log
    
    def no_clicks_query(self):
        #consultas sem nenhum click
        unclicked_queries = []
        for i,q in self.query_log.iterrows():
            if q['id_consulta'] not in self.click_log['id_consulta'].to_list():
                unclicked_queries.append(q.to_dict())
        response = {
            "total": len(unclicked_queries),
            "detailed": unclicked_queries
        }
        return response

    def no_results_query(self):
        #consultas sem nenhum resultado, ou seja,
        #consultas em que a pagina é igual a 1 e a lista de documentos esta vazia
        no_ressults = self.query_log.loc[ (self.query_log['pagina'] == 1) & (self.query_log['documentos'].str.len() == 0) ]
        no_ressults = no_ressults.reset_index(drop=True)
        response = {
            "total":len(no_ressults),
            "data": no_ressults.to_dict(orient='records')
        }
        return response

    def avg_click_position(self):
        #media da posição dos clicks
        response = {
            "avg_click_position": self.click_log['posicao'].mean()
        }
        return response

    def clicks_per_document(self):
        #clicks por documento for every recovered document
        recovered_docs = []
        for docs in self.query_log['documentos']:
            recovered_docs = recovered_docs + docs
        recovered_docs = pd.Series(recovered_docs).drop_duplicates().to_list()

        data = []
        for doc in recovered_docs:
            d = {
                "id_documento": doc
            }
            d["n_clicks"] = len(self.click_log[self.click_log['id_documento'] == doc])
            data.append(d)
        return data

    def clicks_per_position(self):
        #clicks por posição
        data = {
            "clicks_per_position": self.click_log.groupby(by='posicao', as_index=False ).count()[['posicao','id_documento']].to_dict(orient='records')
        }
        return data

    def avg_response_time(self):
        #calcula o tempo de resposta medio geral e o tempo de resposta medio para cada tamanho de consulta para cada algoritimo usado
        #alem de retornar o tempo medio geral, para cada tamanho de query retorna o tempo medio da busca e o numero de consultas para aquele tamanho
        df = pd.DataFrame(self.query_log)
        df['numero_termos'] = df['text_consulta'].apply(lambda x: len(x.replace('"', "").split(" ")))
        avg_times = df.groupby(by = ["algoritmo", "numero_termos", ], as_index =False)["tempo_resposta"].mean()
        response = {
            "total_avg_time": df["tempo_resposta"].mean(),
            "detailed": avg_times.to_dict(orient='records')
        }
        return response

    # def hist_clicks_per_position():
        #     #histograma de clicks por posição
        #     return 

#     #Using join operation - no sense, however it shows how to perform a join operation between both tables
#     def no_clicks_query(self):
#         #consultas sem nenhum click
#         click_join_columns = ["id_documento", "id_consulta", "posicao", "timestamp", "tipo_documento", "pagina"]
#         query_join_columns = ["id_consulta","pagina", "id_sessao", "id_usuario", "text_consulta", "data_hora", "tempo_resposta", "resultados_por_pagina"]
#         query_clicks = self.click_log[click_join_columns].join(self.query_log[query_join_columns].set_index(["id_consulta", 'pagina']), on = ["id_consulta", 'pagina'])
        
#         unclicked_queries = []
#         for i,row in self.query_log.iterrows():
#             if row["id_consulta"] not in query_clicks["id_consulta"].drop_duplicates().to_list():
#                 unclicked_queries.append(row.to_dict())
#         response = {
#             "total": len(unclicked_queries),
#             "detailed": unclicked_queries
#         }
#         return response