from django.urls import path

from . import views

app_name = 'services'
urlpatterns = [
    path('search', views.search, name='search'),
    path('document', views.document, name='document'),
    path('query_suggestion', views.query_suggestion, name='query_suggestion'),
    path('log_search_result_click', views.log_search_result_click, name='log_search_result_click'),
    path('log_query_suggestion_click', views.log_query_suggestion_click, name='log_query_suggestion_click'),
    path('clicks_per_document', views.clicks_per_document, name='clicks_per_document'),
]