from django.urls import path
from . import views

app_name = 'mpmg.services'
urlpatterns = [
    path('login', views.CustomAuthToken.as_view(), name='login'),
    # path('logout', views.do_logout, name='logout'),
    path('search', views.Search.as_view(), name='search'),
    path('document', views.DocumentViewer.as_view(), name='document'),
    path('query_suggestion', views.query_suggestion, name='query_suggestion'),
    path('log_search_result_click', views.log_search_result_click, name='log_search_result_click'),
    path('log_query_suggestion_click', views.log_query_suggestion_click, name='log_query_suggestion_click'),
    path('get_log_buscas', views.get_log_buscas, name='get_log_buscas'),
    path('get_log_clicks', views.get_log_clicks, name='get_log_clicks'),
    path('get_metrics', views.get_metrics, name='get_metrics'),
    path('generate_log_data', views.generate_log_data, name='generate_log_data'),
    path('get_log_sugestoes', views.get_log_sugestoes, name='get_log_sugestoes'),
]