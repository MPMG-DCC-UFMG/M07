from django.urls import path
from . import views

app_name = 'mpmg.services'
urlpatterns = [
    path('login', views.CustomAuthToken.as_view(), name='login'),
    path('logout', views.TokenLogout.as_view(), name='logout'),
    path('search', views.SearchView.as_view(), name='search'),
    path('document', views.DocumentView.as_view(), name='document'),
    path('query_suggestion', views.QuerySuggestionView.as_view(), name='query_suggestion'),
    path('log_search', views.LogSearchView.as_view(), name='log_search'),
    path('log_search_click', views.LogSearchClickView.as_view(), name='log_search_click'),
    path('log_query_suggestion', views.LogQuerySuggestionView.as_view(), name='log_query_suggestion'),
    path('log_query_suggestion_click', views.LogQuerySuggestionClickView.as_view(), name='log_query_suggestion_click'),
    path('metrics', views.MetricsView.as_view(), name='metrics'),
    path('generate_log_data', views.LogDataGeneratorView.as_view(), name='generate_log_data'),
]