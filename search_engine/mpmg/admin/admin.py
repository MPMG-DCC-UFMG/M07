from django.contrib import admin
from django.urls import path
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.conf import settings
from ..services.models import LogSearch
from ..services.models.elastic_model import ElasticModel
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import pandas as pd
from ..services.metrics import Metrics
from .forms import ConfigForm
from ..services.elastic import Elastic
import requests


class CustomAdminSite(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(CustomAdminSite, self).__init__()

  
    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        my_urls = [
            path('log_search/', self.admin_view(self.view_log_search), name='log_search'),
            path('config/', self.admin_view(self.view_config), name='config'),
            path('save_config/', self.admin_view(self.view_save_config), name='save_config'),
        ]
        return my_urls + urls
    
    def index(self, request):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        if start_date != None and end_date != None:
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
        else:
            end_date = datetime.today().date() #+ timedelta(days=1)
            start_date = end_date - timedelta(days=14)
        
        # período das métricas e estatísticas
        start_date_millis = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)
        end_date_millis = int(datetime(year=end_date.year, month=end_date.month, day=end_date.day).timestamp() * 1000)
        days_labels = [d.strftime('%d/%m') for d in pd.date_range(start_date, end_date)]

        # métricas
        metrics = Metrics(start_date, end_date)

        # informação sobre os índices
        indices_info = ElasticModel.get_indices_info()

        # dados para o gráfico de pizza com a qtde de documentos por índice
        searchable_indices = list(settings.SEARCHABLE_INDICES.keys())
        colors = ['#ffcd56', # amarelo
                  '#6ac472', # verde
                  '#ff9f40', # laranja
                  '#36a2eb', # azul
                  '#ff6384'] # rosa
        indices_amounts = {'data':[], 'colors':[], 'labels':[]}
        for item in indices_info:
            if item['index_name'] in searchable_indices:
                indices_amounts['data'].append(item['num_documents'])
                indices_amounts['colors'].append(colors.pop())
                indices_amounts['labels'].append(item['index_name'])
        
        # tempo de resposta médio por dia
        if len(metrics.query_log) > 0:
            mean_response_time = metrics.query_log.groupby(by='dia')['tempo_resposta_total'].mean().round(2).to_dict()
        else:
            mean_response_time = {}
        response_time_per_day = dict.fromkeys(days_labels, 0)
        for k,v in mean_response_time.items():
            if k in response_time_per_day:
                response_time_per_day[k] = v
        
        
        # join com usuários no dataframe
        users = {}
        if len(metrics.query_log) > 0:
            user_ids = metrics.query_log.id_usuario.unique()
            for user in User.objects.filter(id__in=user_ids):
                users[user.id] = {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name}
            metrics.query_log['nome_usuario'] = metrics.query_log['id_usuario'].apply(lambda i: users[i]['first_name'] if i in users else '')
        else:
            user_ids = []
        
        # Buscas por dia
        if len(metrics.query_log) > 0:
            queries_list = metrics.query_log.fillna('-').sort_values(by='data_hora', ascending=False).to_dict('records')
        else:
            queries_list = []
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
        
        # porcentagem sem clique (por dia)
        porc_no_clicks_per_day = {}
        for d, v in no_clicks_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_clicks_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_clicks_per_day[d] = 0
        
        # porcentagem sem resultado (por dia)
        porc_no_results_per_day = {}
        for d, v in no_results_per_day.items():
            if total_queries_per_day[d] != 0:
                porc_no_results_per_day[d] = round(v/total_queries_per_day[d]*100)
            else:
                porc_no_results_per_day[d] = 0
        
        # totais
        if len(metrics.query_log) > 0:
            total_queries = metrics.query_log.id.value_counts().sum()
            total_no_clicks = no_clicks['no_clicks_query']
            total_no_results = no_results['no_results_query']
            porc_total_no_clicks = int(total_no_clicks / total_queries * 100)
            porc_total_no_results = int(total_no_results / total_queries * 100)
            avg_query_time = round(metrics.query_log.tempo_resposta_total.mean(), 2)
        else:
            total_queries = 0
            total_no_clicks = 0
            total_no_results = 0
            porc_total_no_clicks = 0
            porc_total_no_results = 0
            avg_query_time = 0

        context = dict(
            self.each_context(request), # admin variables
            start_date= start_date.strftime('%d/%m/%Y'),
            end_date= end_date.strftime('%d/%m/%Y'),
            total_queries= total_queries,
            avg_query_time= avg_query_time,
            total_no_clicks= total_no_clicks,
            total_no_results= total_no_results,
            porc_total_no_clicks= porc_total_no_clicks,
            porc_total_no_results= porc_total_no_results,
            indices_info= indices_info,
            indices_amounts= indices_amounts,
            total_searches_per_day= {'labels': list(total_queries_per_day.keys()), 'data': list(total_queries_per_day.values())},
            response_time_per_day= {'labels': list(response_time_per_day.keys()), 'data': list(response_time_per_day.values())},
            last_queries= queries_list[:10],
            no_clicks_per_day= {'labels': list(no_clicks_per_day.keys()), 'data': list(no_clicks_per_day.values())},
            no_results_per_day= {'labels': list(no_results_per_day.keys()), 'data': list(no_results_per_day.values())},
            porc_no_clicks_per_day= {'labels': list(porc_no_clicks_per_day.keys()), 'data': list(porc_no_clicks_per_day.values())},
            porc_no_results_per_day= {'labels': list(porc_no_results_per_day.keys()), 'data': list(porc_no_results_per_day.values())},
        )
        return render(request, 'admin/index.html', context)
    

    def view_log_search(self, request):
        id_sessao = request.GET.get('id_sessao', '')
        id_consulta = request.GET.get('id_consulta', '')
        id_usuario = request.GET.get('id_usuario', '')
        text_consulta = request.GET.get('text_consulta', '')
        algoritmo = request.GET.get('algoritmo', '')
        page = int(request.GET.get('page', 1))
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        tempo = request.GET.get('tempo', '')
        tempo_op = request.GET.get('tempo_op')

        total_records, log_buscas_list = LogSearch.get_list_filtered(
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            page=page, 
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            sort={'data_hora':{'order':'desc'}}
        )

        total_pages = (total_records // self.results_per_page) + 1

        url_params = "&id_sessao=%s&id_consulta=%s&id_usuario=%s"\
                    "&text_consulta=%s&algoritmo=%s&start_date=%s"\
                    "&end_date=%s&tempo=%s&tempo_op=%s"\
                    % (id_sessao, id_consulta, id_usuario,\
                    text_consulta, algoritmo, start_date, end_date, tempo, tempo_op)

        context = dict(
            self.each_context(request), # admin template variables.
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            result_list=log_buscas_list,
            page=page,
            total_records=total_records,
            results_per_page=self.results_per_page,
            total_pages=total_pages,
            pagination_items=range(min(9, total_pages)),
            url_params=url_params,
        )
        
        return render(request, 'admin/log_search.html', context)

    def view_config(self, request):
        es = Elastic()
        current_algo = es.get_cur_algo()
        form = ConfigForm(initial={'algorithm': current_algo})

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            form = form,
        )
        
        return render(request, 'admin/config.html', context)

    def view_save_config(self, request):
        # TODO: Enviar requests pro ES pra realmente efetivar as mudanças escolhidas
        algorithm = request.POST['algorithm']

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
        )
        
        return redirect(reverse('admin:config'))

custom_admin_site = CustomAdminSite()

custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)