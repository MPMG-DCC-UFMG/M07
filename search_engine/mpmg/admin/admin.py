import requests
from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from mpmg.admin.views import *


class AdunaAdmin(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(AdunaAdmin, self).__init__()

  
    def get_urls(self):
        native_urls = super(AdunaAdmin, self).get_urls()
        new_urls = [
            path('', self.admin_view(DashboardView().view_dashboard), name='index'),
            path('log_search/', self.admin_view(LogSearchView().view_log_search), name='log_search'),
            path('log_search_detail/', self.admin_view(LogSearchView().view_detail), name='log_search_detail'),
            path('log_click/', self.admin_view(LogSearchClickView().view_log_click), name='log_search_click'),
            path('config/', self.admin_view(ConfigView().view_config), name='config'),
            path('save_config/', self.admin_view(ConfigView().view_save_config), name='save_config'),

            path('search_configs/', SearchConfigsView().view_search_configs , name='search_configs'),  
            path('add_weighted_search_field/',SearchConfigsView().view_add_weighted_search_field , name='add_weighted_search_field'),  
            path('update_weighted_search_field/<str:field>', SearchConfigsView().view_update_weighted_search_field , name='update_weighted_search_field'),  
            path('destroy_weighted_search_field/<str:field>', SearchConfigsView().view_destroy_weighted_search_field , name='destroy_weighted_search_field'),  

            path('update_searchable_indice/<str:index>',SearchConfigsView().view_update_searchable_indice , name='update_searchable_indice'),  
            path('destroy_searchable_indice/<str:index>',SearchConfigsView().view_destroy_searchable_indice , name='destroy_searchable_indice'),  
            path('add_searchable_indice/',SearchConfigsView().view_add_searchable_indice , name='add_searchable_indice'),  
        ]
        return new_urls + native_urls
    
    

custom_admin_site = AdunaAdmin()
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)