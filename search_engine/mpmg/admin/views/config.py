from django.contrib import admin
from django.urls import path
from django.urls import reverse
from django.shortcuts import render, redirect
from mpmg.admin.forms import ConfigForm
from mpmg.services.elastic import Elastic

class ConfigView(admin.AdminSite):

    def __init__(self):
        super(ConfigView, self).__init__()

    def view_config(self, request):
        es = Elastic()
        current_algo = es.get_cur_algo()
        form = ConfigForm(initial={'algorithm': current_algo})

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            form = form,
        )
        
        return render(request, 'admin/config.html', context)

    def view_save_config(self, request):
        # TODO: Enviar requests pro ES pra realmente efetivar as mudanças escolhidas
        algorithm = request.POST['algorithm']

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
        )
        
        return redirect(reverse('admin:config'))