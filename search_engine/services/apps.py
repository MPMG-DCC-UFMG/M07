from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class ServicesConfig(AppConfig):
    name = 'services'


class CustomAdminConfig(AdminConfig):
    default_site = 'services.admin.CustomAdminSite'
