from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView, DetailView
from asset import models as asset_models
from host import models as host_models
import django_filters
from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .models import UserLoginLog

class FilteredListView(ListView):
    filterset_class = None

    def param_replace(self):
        # 支持分頁器
        data = self.request.GET.copy()
        if self.page_kwarg in data.keys():
            data.pop(self.page_kwarg)

        return {k: v for k, v in data.items() if v}

    def get_queryset(self):
        queryset = super().get_queryset()

        get = self.request.GET.copy()

        self.filterset = self.filterset_class(get, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get('contacts'):
            self.paginate_by = int(self.request.GET.get('contacts', 10))
        context['filterset'] = self.filterset
        context['search_field'] = self.param_replace()
        context['page_list'] = [2,10, 20, 50, 100]
        return context




class LoginListFilter(django_filters.FilterSet):

    class Meta:
        model = UserLoginLog
        fields = '__all__'

# class PeriodicTaskListFilter(django_filters.FilterSet):
#
#     class Meta:
#         model = djcelery_model.PeriodicTask
#         fields = '__all__'
