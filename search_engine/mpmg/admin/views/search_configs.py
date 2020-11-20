from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import reverse
from mpmg.admin.forms import AddWeightedSearchFieldForm, EditWeightedSearchFieldForm, AddSearchableIndexForm, EditSearchableIndexForm, SearchConfigsForm
from mpmg.services.models import WeightedSearchFieldsConfigs, SearchableIndicesConfigs, SearchConfigs


class SearchConfigsView(admin.AdminSite): 
    def __init__(self):
        super(SearchConfigsView, self).__init__()
        
    def view_search_configs(self, request):  
        weighted_search_fields = WeightedSearchFieldsConfigs.objects.all()  
        searchable_indices = SearchableIndicesConfigs.objects.all()
        
        if request.method == "POST":  
            form_search_configs =  SearchConfigsForm(request.POST)
            if form_search_configs.is_valid():  
                form_search_configs.save()  
                return redirect(reverse('admin:search_configs'))
                
        initial = {
            'results_per_page': SearchConfigs().get_results_per_page(),
            'use_entities_in_search': SearchConfigs().get_use_entities_in_search(),
        }
        form_search_configs =  SearchConfigsForm(initial=initial)
        context = {
            'weighted_search_fields':weighted_search_fields,
            'searchable_indices': searchable_indices,
            'form_search_configs': form_search_configs
        }
        return render(request,"admin/search_configs.html", context)  


    def view_add_searchable_indice(self, request):
        if request.method == "POST":  
            form = AddSearchableIndexForm(request.POST)  
            if form.is_valid():  
                try:  
                    form.save()  
                    return redirect(reverse('admin:search_configs'))
                except:  
                    pass  
        else:  
            form = AddSearchableIndexForm()  
        return render(request,'admin/add_searchable_indice.html',{'form':form})  

    def view_update_searchable_indice(self, request, index):
        searchable_index = SearchableIndicesConfigs.objects.get(index=index)  
        if request.method == "POST":
            form = EditSearchableIndexForm(request.POST) 
            if form.is_valid():  
                searchable_index.searchable = form.cleaned_data['searchable']
                searchable_index.group = form.cleaned_data['group']
                searchable_index.save()
                return redirect(reverse('admin:search_configs'))
        else:
            form = EditSearchableIndexForm(initial = {'searchable': searchable_index.searchable })  
        return render(request, 'admin/update_searchable_indice.html', {'searchable_index': searchable_index, 'form': form})  
    
    def view_destroy_searchable_indice(self, request, index):
        searchable_index = SearchableIndicesConfigs.objects.get(index=index)  
        searchable_index.delete()  
        return redirect(reverse('admin:search_configs'))


    def view_add_weighted_search_field(self, request):  
        if request.method == "POST":  
            form = AddWeightedSearchFieldForm(request.POST)  
            if form.is_valid():  
                try:  
                    form.save()  
                    return redirect(reverse('admin:search_configs'))
                except:  
                    pass  
        else:  
            form = AddWeightedSearchFieldForm()  
        return render(request,'admin/add_weighted_search_field.html',{'form':form})  

    def view_update_weighted_search_field(self, request, field): 
        weighted_search_field = WeightedSearchFieldsConfigs.objects.get(field=field)  
        if request.method == "POST":
            form = EditWeightedSearchFieldForm(request.POST) 
            if form.is_valid():  
                weighted_search_field.weight = form.cleaned_data['weight']
                weighted_search_field.searchable = form.cleaned_data['searchable']
                weighted_search_field.save()
                return redirect(reverse('admin:search_configs'))
        else:
            form = EditWeightedSearchFieldForm(initial = {'weight': weighted_search_field.weight, 'searchable': weighted_search_field.searchable })  
        return render(request, 'admin/update_weighted_search_field.html', {'weighted_search_field': weighted_search_field, 'form': form})  

    def view_destroy_weighted_search_field(self, request, field):  
        weighted_search_field = WeightedSearchFieldsConfigs.objects.get(field=field)  
        weighted_search_field.delete()  
        return redirect(reverse('admin:search_configs'))


       
            

        # def view_search_configs(self, request):

        #     form = SearchConfigsForm()

        #     context = dict(
        #         self.each_context(request), # Include common variables for rendering the admin template.
        #         form = form,
        #     )
            
        #     return render(request, 'admin/search_configs.html', context)

        # def view_save_search_configs(self, request):
            
        #     return redirect(reverse('admin:config'))