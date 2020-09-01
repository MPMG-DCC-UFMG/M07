from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import LogSearch

class LogSearchView(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(LogSearchView, self).__init__()
    
    def view_log_search(self, request):
        results_per_page = int(request.GET.get('results_per_page', self.results_per_page))
        id_sessao = request.GET.get('id_sessao', '')
        id_consulta = request.GET.get('id_consulta', '')
        id_usuario = request.GET.get('id_usuario', '')
        text_consulta = request.GET.get('text_consulta', '')
        algoritmo = request.GET.get('algoritmo', '')
        page = int(request.GET.get('page', 1))
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        tempo = request.GET.get('tempo', '')
        tempo_op = request.GET.get('tempo_op')
        self.results_per_page = results_per_page
        print(request.GET)
        LogSearch.results_per_page = self.results_per_page
        total_records, log_buscas_list = LogSearch.get_list_filtered(
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            page=page, 
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            sort={'data_hora':{'order':'desc'}}
        )

        total_pages = (total_records // self.results_per_page) + 1

        url_params = "&id_sessao=%s&id_consulta=%s&id_usuario=%s"\
                    "&text_consulta=%s&algoritmo=%s&start_date=%s"\
                    "&end_date=%s&tempo=%s&tempo_op=%s"\
                    % (id_sessao, id_consulta, id_usuario,\
                    text_consulta, algoritmo, start_date, end_date, tempo, tempo_op)

        context = dict(
            self.each_context(request), # admin template variables.
            id_sessao=id_sessao,
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            text_consulta=text_consulta,
            algoritmo=algoritmo,
            start_date=start_date,
            end_date=end_date,
            tempo=tempo,
            tempo_op=tempo_op,
            result_list=log_buscas_list,
            page=page,
            total_records=total_records,
            results_per_page=self.results_per_page,
            total_pages=total_pages,
            pagination_items=range(min(9, total_pages)),
            url_params=url_params,
        )
        
        return render(request, 'admin/log_search.html', context)
