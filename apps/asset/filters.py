from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView, DetailView
from asset import models as asset_models
from host import models as host_models
import django_filters
from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType



class AssetListFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains',label='名稱')
    content_type = django_filters.ModelChoiceFilter(
        queryset=ContentType.objects.filter(model__in=['networkdevice', 'host']),
        label='類型'
    )


    class Meta:
        model = asset_models.Asset
        fields = ['name','rack', 'device_status_id', 'tag', 'content_type']


class NetworkDeviceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='設備名稱')

    class Meta:
        model = asset_models.NetworkDevice
        fields = ['name', 'manage_ip', 'sub_asset_type']


class IdracListFilter(django_filters.FilterSet):
    idrac_ip = django_filters.CharFilter(lookup_expr='icontains', label='IP')

    status = django_filters.TypedChoiceFilter(choices=(('', '----'), ('false', '連接中'), ('true', '連接成功'),), label='狀態')

    def filter_queryset(self, queryset):
        for i in self._meta.exclude:
            self.form.cleaned_data.pop(i)
        return super().filter_queryset(queryset=queryset)

    class Meta:
        model = host_models.idrac
        fields = ['idrac_ip']
        exclude = ['status']

class RunUserListFilter(django_filters.FilterSet):

    class Meta:
        model = host_models.RunUser
        fields = ['name']

class HostRecordListFilter(django_filters.FilterSet):

    class Meta:
        model = host_models.HostRecord
        fields = '__all__'

class CmdRecordListFilter(django_filters.FilterSet):

    class Meta:
        model = host_models.CmdRecord
        fields = '__all__'


class HostListFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='主機名稱')
    manage_ip = django_filters.CharFilter(lookup_expr='icontains', label='IP')
    enabled = django_filters.TypedChoiceFilter(choices=(('', '------'), (False, '新發現'), (True, '啟用'),), label='狀態')

    class Meta:
        model = host_models.Host
        fields = ['name', 'manage_ip', 'enabled', 'node']


class IDCListFilter(django_filters.FilterSet):


    class Meta:
        model = asset_models.IDC
        fields = '__all__'


class ISPListFilter(django_filters.FilterSet):

    class Meta:
        model = asset_models.ISP
        fields = '__all__'

class RackListFilter(django_filters.FilterSet):

    class Meta:
        model = asset_models.Rack
        fields = '__all__'

from django_celery_beat import models as djcelery_model

class PeriodicTaskListFilter(django_filters.FilterSet):

    class Meta:
        model = djcelery_model.PeriodicTask
        fields = '__all__'

