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
        sim_settings = self.es.get_cur_algo(group='regular') #TODO: acertar isso para obter da interface
        current_num_repl = self.es.get_cur_replicas()
        max_result_window = self.es.get_max_result_window()
        algo = sim_settings['type']
        initial = {'algorithm': algo, 
                   'num_repl': current_num_repl,
                   'max_result_window': max_result_window,}

        # Settings específicos por algoritmo
        if algo == 'BM25':
            initial['k1'] = sim_settings['k1']
            initial['b'] = sim_settings['b']
            initial['discount_overlaps'] = sim_settings['discount_overlaps']
        elif algo == 'DFR':
            initial['basic_model'] = sim_settings['basic_model']
            initial['after_effect'] = sim_settings['after_effect']
            normalization = sim_settings['normalization']
            initial['normalization_dfr'] = normalization
            # O nome do parâmetro muda a depender da normalização, assim conseguimos pegar independente do nome
            # Só o parâmetro de normalização é representado com dict
            if normalization != 'no':
                normalization_parameter = [x for x in sim_settings.values() if type(x) == dict][0] 
                initial['normalization_parameter_dfr'] = list(normalization_parameter.values())[0] 
        elif algo == 'DFI':
            initial['independence_measure'] = sim_settings['independence_measure']
        elif algo == 'IB':
            initial['distribution'] = sim_settings['distribution']
            initial['lambda_ib'] = sim_settings['lambda']
            normalization = sim_settings['normalization']
            initial['normalization_ib'] = normalization
            # O nome do parâmetro muda a depender da normalização, assim conseguimos pegar independente do nome
            # Só o parâmetro de normalização é representado com dict
            if normalization != 'no':
                normalization_parameter = [x for x in sim_settings.values() if type(x) == dict][0] 
                initial['normalization_parameter_ib'] = list(normalization_parameter.values())[0] 
        elif algo == 'LMDirichlet':
            initial['mu'] = sim_settings['mu']
        elif algo == 'LMJelinek':
            initial['lambda_jelinek'] = sim_settings['lambda']


        form = ConfigForm(initial=initial)

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            form = form,
        )
        
        return render(request, 'admin/config.html', context)

    def view_save_config(self, request):
        # algo = request.POST['algorithm']
        num_repl = request.POST['num_repl']
        max_result_window = request.POST['max_result_window']
        params_dict = request.POST.dict()
        self.es.set_cur_algo(**params_dict)
        self.es.set_cur_replicas(num_repl)
        self.es.set_max_result_window(max_result_window)
        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
        )
        
        return redirect(reverse('admin:config'))