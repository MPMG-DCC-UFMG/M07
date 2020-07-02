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
        log_buscas_list = LogBusca.get_list(sort={'data_hora':{'order':'desc'}})

        context = dict(
           self.each_context(request), # Include common variables for rendering the admin template.
           result_list=log_buscas_list,
        )
        
        return render(request, 'admin/log_buscas.html', context)


custom_admin_site = CustomAdminSite()

custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)