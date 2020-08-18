from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.conf import settings
from mpmg.services.models import LogSearch
from mpmg.services.models import ElasticModel
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import pandas as pd
from .metrics import Metrics


class CustomAdminSite(admin.AdminSite):

    def __init__(self):
        super(CustomAdminSite, self).__init__()

  
    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        my_urls = [
            path('log_search/', self.admin_view(self.view_log_search)),
        ]
        return my_urls + urls
    
    def index(self, request):
        # período das métricas e estatísticas
        end_date = datetime.today().date() #+ timedelta(days=1)
        start_date = end_date - timedelta(days=14)
        start_date_millis = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)
        end_date_millis = int(datetime(year=end_date.year, month=end_date.month, day=end_date.day).timestamp() * 1000)
        days_labels = [d.strftime('%d/%m') for d in pd.date_range(start_date, end_date)]

        # métricas
        metrics = Metrics(start_date, end_date)

        # informação sobre os índices
        indices_info = ElasticModel.get_indices_info()

        # users = User.objects.all()

        # totais
        total_queries = metrics.query_log.id.value_counts().sum()
        print(metrics.query_log.columns)
        avg_query_time = round(metrics.query_log.tempo_resposta_total.mean(), 2)
        
        # dados para o gráfico de pizza com a qtde de documentos por índice
        searchable_indices = list(settings.SEARCHABLE_INDICES.keys())
        colors = ['#ffcd56', '#4bc0c0', '#ff9f40', '#36a2eb', '#ff6384']
        indices_amounts = {'data':[], 'colors':[], 'labels':[]}
        for item in indices_info:
            if item['index_name'] in searchable_indices:
                indices_amounts['data'].append(item['num_documents'])
                indices_amounts['colors'].append(colors.pop())
                indices_amounts['labels'].append(item['index_name'])
        
        # Buscas por dia
        queries_list = metrics.query_log.fillna('-').to_dict('records')
        total_queries_per_day = dict.fromkeys(days_labels, 0)
        for item in queries_list:
            d = item['dia']
            if d in total_queries_per_day:
                total_queries_per_day[d] += 1

        # Consultas sem clique por dia
        no_clicks = metrics.no_clicks_query()
        no_clicks_per_day = dict.fromkeys(days_labels, 0)
        for item in no_clicks['detailed']:
            d = item['dia']
            if d in no_clicks_per_day:
                no_clicks_per_day[d] += 1
        
        # Consultas sem resultado
        no_results = metrics.no_results_query()
        no_results_per_day = dict.fromkeys(days_labels, 0)
        for item in no_results['detailed']:
            d = item['dia']
            if d in no_results_per_day:
                no_results_per_day[d] += 1
        
        # porcentagens
        porc_no_clicks_per_day = {}
        for d, v in no_clicks_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_clicks_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_clicks_per_day[d] = 0
        
        porc_no_results_per_day = {}
        for d, v in no_results_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_results_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_results_per_day[d] = 0
        

        context = {
            'total_queries': total_queries,
            'avg_query_time': avg_query_time,
            'indices_info': indices_info,
            'indices_amounts': indices_amounts,
            'total_searches_per_day': {'labels': list(total_queries_per_day.keys()), 'data': list(total_queries_per_day.values())},
            'last_queries': queries_list[:10],
            'no_clicks_per_day': {'labels': list(no_clicks_per_day.keys()), 'data': list(no_clicks_per_day.values())},
            'no_results_per_day': {'labels': list(no_results_per_day.keys()), 'data': list(no_results_per_day.values())},
            'porc_no_clicks_per_day': {'labels': list(porc_no_clicks_per_day.keys()), 'data': list(porc_no_clicks_per_day.values())},
            'porc_no_results_per_day': {'labels': list(porc_no_results_per_day.keys()), 'data': list(porc_no_results_per_day.values())},
        }
        return render(request, 'admin/index.html', context)
    

    def view_log_search(self, request):
        id_sessao = request.GET.get('id_sessao', None)
        id_consulta = request.GET.get('id_consulta', None)
        id_usuario = request.GET.get('id_usuario', None)
        text_consulta = request.GET.get('text_consulta', None)
        page = request.GET.get('page', 1)

        total_records, log_buscas_list = LogSearch.get_list_filtered(
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            page=page, 
            sort={'data_hora':{'order':'desc'}}
        )

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            page=page,
            total_records=total_records,
            result_list=log_buscas_list,
        )
        
        return render(request, 'admin/log_search.html', context)


custom_admin_site = CustomAdminSite()

custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)