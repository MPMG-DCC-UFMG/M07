from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'aduna'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('document/<str:doc_type>/<str:doc_id>', views.document, name='document'),
    path('login', views.login_view, name='login'),
    path('efetua_login', views.efetua_login, name='efetua_login'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)