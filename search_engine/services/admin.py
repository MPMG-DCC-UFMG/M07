from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from services.models import LogBusca


class CustomAdminSite(admin.AdminSite):

    def __init__(self):
        super(CustomAdminSite, self).__init__()

  
    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        my_urls = [
            path('log_buscas/', self.admin_view(self.view_log_buscas)),
        ]
        return my_urls + urls
    

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