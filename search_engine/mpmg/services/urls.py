from django.urls import path
from . import views

app_name = 'mpmg.services'
urlpatterns = [
    path('login', views.CustomAuthToken.as_view(), name='login'),
    # path('logout', views.do_logout, name='logout'),
    path('search', views.Search.as_view(), name='search'),
    path('document', views.DocumentViewer.as_view(), name='document'),
    path('query_suggestion', views.query_suggestion, name='query_suggestion'),
    path('log_search', views.LogSearchView.as_view(), name='log_search'),
    path('log_search_click', views.LogSearchClickView.as_view(), name='log_search_click'),
    path('log_suggestion', views.LogSuggestionView.as_view(), name='log_suggestion'),
    path('log_suggestion_click', views.LogSuggestionClickView, name='log_suggestion_click'),
    path('get_metrics', views.get_metrics, name='get_metrics'),
    path('generate_log_data', views.LogDataGeneratorView.as_view(), name='generate_log_data'),
]