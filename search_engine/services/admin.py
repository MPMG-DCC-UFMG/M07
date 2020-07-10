from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.conf import settings
from services.models import LogBusca
from services.models import ElasticModel
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import pandas as pd


class CustomAdminSite(admin.AdminSite):

    def __init__(self):
        super(CustomAdminSite, self).__init__()

  
    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        my_urls = [
            path('log_buscas/', self.admin_view(self.view_log_buscas)),
        ]
        return my_urls + urls
    
    def index(self, request):
        # informação sobre os índices
        indices_info = ElasticModel.get_indices_info()

        # users = User.objects.all()
        
        # dados para o gráfico de pizza com a qtde de documentos por índice
        searchable_indices = list(settings.SEARCHABLE_INDICES.keys())
        colors = ['#ffcd56', '#4bc0c0', '#ff9f40', '#36a2eb', '#ff6384']
        indices_amounts = {'data':[], 'colors':[], 'labels':[]}
        for item in indices_info:
            if item['index_name'] in searchable_indices:
                indices_amounts['data'].append(item['num_documents'])
                indices_amounts['colors'].append(colors.pop())
                indices_amounts['labels'].append(item['index_name'])
        
        # Consultas da última semana
        end_date = datetime.today().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=7)
        start_date = int(datetime(year=start_date.year, month=start_date.month, day=start_date.day).timestamp() * 1000)
        end_date = int(datetime(year=end_date.year, month=end_date.month, day=end_date.day).timestamp() * 1000)
        _, last_queries = LogBusca.get_list_filtered(start_date=start_date, end_date=end_date, sort={'data_hora':{'order':'desc'}})
        last_queries = pd.DataFrame.from_dict(last_queries)
        last_queries['dia'] = last_queries['data_hora'].apply(lambda v: datetime.fromtimestamp(v/1000).date().strftime('%d/%m'))
        total_searches_per_day = last_queries.groupby(by='dia', as_index=False).count()[['dia', 'id']]
        total_searches_per_day.columns = ['dia', 'total']
        
        context = {
            'indices_info': indices_info,
            'indices_amounts': indices_amounts,
            'total_searches_per_day': {'labels': total_searches_per_day['dia'].to_list(), 'data': total_searches_per_day['total'].to_list()},
            'last_queries': last_queries.head(10).fillna('-').to_dict('records'),
        }
        return render(request, 'admin/index.html', context)
    

    def view_log_buscas(self, request):
        id_sessao = request.GET.get('id_sessao', None)
        id_consulta = request.GET.get('id_consulta', None)
        id_usuario = request.GET.get('id_usuario', None)
        text_consulta = request.GET.get('text_consulta', None)
        page = request.GET.get('page', 1)

        total_records, log_buscas_list = LogBusca.get_list_filtered(
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
        
        return render(request, 'admin/log_buscas.html', context)


custom_admin_site = CustomAdminSite()

custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)