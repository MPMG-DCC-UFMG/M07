from django.contrib import admin
from django.urls import path
from django.urls import reverse
from django.shortcuts import render, redirect
from mpmg.admin.forms import ConfigForm
from mpmg.services.elastic import Elastic

class ConfigView(admin.AdminSite):

    def __init__(self):
        super(ConfigView, self).__init__()
        self.es = Elastic()

    def view_config(self, request):
        current_algo = self.es.get_cur_algo()
        current_num_repl = self.es.get_cur_replicas()
        max_result_window = self.es.get_max_result_window()
        form = ConfigForm(initial={'algorithm': current_algo, 
                                   'num_repl': current_num_repl,
                                   'max_result_window': max_result_window,
                        })

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            form = form,
        )
        
        return render(request, 'admin/config.html', context)

    def view_save_config(self, request):
        # TODO: Salvar algoritmo escolhido
        algorithm = request.POST['algorithm']
        num_repl = request.POST['num_repl']
        max_result_window = request.POST['max_result_window']
        self.es.set_cur_algo()
        self.es.set_cur_replicas(num_repl)
        self.es.set_max_result_window(max_result_window)
        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
        )
        
        return redirect(reverse('admin:config'))