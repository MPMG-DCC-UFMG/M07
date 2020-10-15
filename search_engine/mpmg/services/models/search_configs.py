from django.db import models

class SearchConfigs(models.Model):
    results_per_page = models.IntegerField(default=10, blank=False)
    
    def save(self, *args, **kwargs):
        if SearchConfigs.objects.count() > 0:
            SearchConfigs.objects.all()[0].delete()
        super(SearchConfigs, self).save(*args, **kwargs)

    @classmethod
    def get_results_per_page(cls):
        if SearchConfigs.objects.count() == 0:
            return None
        else:
            return cls.objects.all()[0].results_per_page

class SearchableIndicesConfigs(models.Model):
    index = models.CharField(max_length=50, blank=False, primary_key=True)
    index_model = models.CharField(max_length=50, blank=False)
    searchable = models.BooleanField(default=True, blank=False)
    
    @classmethod
    def get_searchble_indices(cls):
        searchble_indices = []
        for index in cls.objects.all():
            if index.searchable:
                searchble_indices.append(index.index)
        return searchble_indices

    @classmethod
    def get_indices_list(cls):
        return [index.index for index in cls.objects.all()]

    @classmethod
    def get_index_model_class_name(cls, index):
        model = cls.objects.get(index = index ).index_model
        return model

class WeightedSearchFieldsConfigs(models.Model):
    field = models.CharField(max_length=50, blank=False, primary_key=True)
    field_name = models.CharField(max_length=50, blank=False)
    weight = models.IntegerField(default=1, blank=False)
    searchable = models.BooleanField(default=True, blank=False)

    @classmethod
    def get_weigted_search_fields(cls):
        fields_n_weights = []
        for weigted_field in cls.objects.all():
            if weigted_field.searchable:
                fields_n_weights.append(weigted_field.field+"^"+str(weigted_field.weight))
        return fields_n_weights
