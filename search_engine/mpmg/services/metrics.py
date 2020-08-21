import pandas as pd
import time
from datetime import datetime
import requests
from mpmg.services.models import LogSearch, LogSearchClick, LogSugestoes


class Metrics:
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date 
        self.end_date = end_date
        self.query_log, self.click_log, self.sugestion_log = self._get_logs()
        

    def _get_logs(self):
        _, query_log = LogSearch.get_list_filtered(start_date=self.start_date, end_date=self.end_date)
        query_log = pd.DataFrame.from_dict(query_log)
        
        _, sugestion_log = LogSugestoes.get_list_filtered(start_date=self.start_date, end_date=self.end_date)
        sugestion_log = pd.DataFrame.from_dict(sugestion_log)

        # create columns to help on grouping
        if len(query_log) > 0:
            query_log['dia'] = query_log['data_hora'].apply(lambda v: datetime.fromtimestamp(v/1000).date().strftime('%d/%m'))

            id_consultas = query_log['id_consulta'].to_list()

            _, click_log = LogSearchClick.get_list_filtered(id_consultas=id_consultas)
            click_log = pd.DataFrame.from_dict(click_log)
        else:
            click_log = pd.DataFrame.from_dict({})

        return query_log, click_log, sugestion_log
    

    def no_clicks_query(self):
        # consultas com resultado, mas sem nenhum click
        unclicked_queries = []
        for i,q in self.query_log.iterrows():
            if len(q['documentos']) > 0:
                if len(self.click_log) > 0 and q['id_consulta'] not in self.click_log['id_consulta'].to_list():
                    unclicked_queries.append(q.to_dict())
        response = {
            "no_clicks_query": len(unclicked_queries),
            "detailed": unclicked_queries
        }
        return response

    def no_results_query(self):
        #consultas sem nenhum resultado, ou seja,
        #consultas em que a pagina é igual a 1 e a lista de documentos esta vazia
        if len(self.query_log) > 0:
            no_ressults = self.query_log.loc[ (self.query_log['pagina'] == 1) & (self.query_log['documentos'].str.len() == 0) ]
            no_ressults = no_ressults.reset_index(drop=True)
        else:
            no_ressults = pd.DataFrame.from_dict({})
        response = {
            "no_results_query":len(no_ressults),
            "detailed": no_ressults.to_dict(orient='records')
        }
        return response

    def avg_click_position(self):
        #media da posição dos clicks
        response = {
            "avg_click_position": self.click_log['posicao'].astype(int).mean()
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
            
        response = {
            "clicks_per_document": data
        }
        return response

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
            "avg_response_time": df["tempo_resposta"].astype(int).mean(),
            "detailed": avg_times.to_dict(orient='records')
        }
        return response

    def avg_time_to_first_click(self):
        #Calcula o tempo medio ate o primeiro click
        queries = self.query_log['id_consulta'].drop_duplicates().to_list() #calcular todas as queries
        times = []
        for q in queries:
            target_queries = self.query_log[self.query_log['id_consulta'] == q]
            target_queries = target_queries.sort_values(by='data_hora').reset_index(drop=True)
            first_query = target_queries['data_hora'][0]

            if q in self.click_log["id_consulta"].to_list():
                clicks = self.click_log[self.click_log['id_consulta'] == q]
                clicks = clicks.sort_values(by='timestamp', ).reset_index(drop=True)
                first_click = clicks['timestamp'][0]

                time_to_click = first_click - first_query
                times.append(time_to_click)

        response = {
            "avg_time_to_first_click": pd.Series(times).astype(int).mean()
        }
        return response

    def avg_sugestions_click_position(self):
        #media da posição dos clicks das sugestoes
        response = {
            "avg_sugestions_click_position": self.sugestion_log['posicao'].astype(int).mean()
        }
        return response
    
    def clicks_per_sugestion(self):

        sugestions = self.sugestion_log[['sugestao', 'id']].groupby(by='sugestao', as_index = False).count().rename(index=str,columns={'id':'clicks'})

        response = {
            "clicks_per_sugestion": sugestions.to_dict(orient='records')
        }
        return response

    

   