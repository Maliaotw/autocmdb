from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from . import models
from . import forms
from asset import models as asset_models
from asset import filters
from src.base.views import FilteredListView


class HostListView(FilteredListView):
    model = models.Host
    paginate_by = 10
    template_name = 'bus/host_list.html'
    filterset_class = filters.HostListFilter

    def post(self, request, *args, **kwargs):

        host = self.request.POST.get('host')
        host_obj = models.Host.objects.get(id=host)
        asset_models.Asset.objects.create(content_object=host_obj)
        host_obj.enabled = True
        host_obj.save()

        return JsonResponse({'msg': '成功'})

    def get_queryset(self):

        self.paginate_by = 10
        obj = super().get_queryset().filter(cate=2).order_by('-latest_date')

        searchdata = {}
        for i in ['node__name', 'page', 'cate']:

            if self.request.GET.get(i):
                if i == 'page':
                    pass
                else:
                    searchdata[i] = self.request.GET.get(i)

        obj = obj.filter(**searchdata)

        self.searchdata = searchdata

        return obj


class HostDetailView(DetailView):
    model = models.Host
    template_name = 'bus/host_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if not obj.enabled:
            obj.enabled = True
            obj.save()

        return obj

    def get_context_data(self, **kwargs):
        hp = models.HostProc.objects.filter(host=self.object).last()
        hn = models.HostNet.objects.filter(host=self.object).last()
        context = {
            "proc_list": hp.proc.all() if hp else '',
            "net_list": hn.net.all() if hn else ''
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class BusinessunitListView(ListView):
    model = models.BusinessUnit
    paginate_by = 10
    template_name = 'bus/businessunit_list.html'


class BusinessunitCreateView(CreateView):
    model = models.BusinessUnit
    form_class = forms.BusUnitFrom
    template_name = 'bus/businessunit_form.html'
    success_url = reverse_lazy("host:busunit-list")


class BusinessunitUpdateView(UpdateView):
    model = models.BusinessUnit
    form_class = forms.BusUnitFrom
    success_url = reverse_lazy("host:busunit-list")
    template_name = 'bus/businessunit_form.html'


class BusinessunitDeleteView(DeleteView):
    model = models.BusinessUnit
    template_name = 'bus/businessunit_list.html'
    success_url = reverse_lazy("host:busunit-list")


class HostRecordListView(FilteredListView):
    template_name = 'audits/hostrecord_list.html'
    model = models.HostRecord
    filterset_class = filters.HostRecordListFilter
    paginate_by = 10


class CmdRecordLiewView(FilteredListView):
    model = models.CmdRecord
    paginate_by = 10
    filterset_class = filters.CmdRecordListFilter
    template_name = 'audits/cmdrecord_list.html'


class RunUserListView(FilteredListView):
    model = models.RunUser
    paginate_by = 10
    filterset_class = filters.RunUserListFilter
    template_name = 'task/runuser-list.html'

class RunuserCreateView(CreateView):
    model = models.RunUser
    template_name = 'task/runuser-form.html'
    form_class = forms.RunUserForm
    success_url = reverse_lazy('host:runuser-list')

    def post(self,request,*args,**kwargs):
        return super(RunuserCreateView, self).post(request,*args,**kwargs)


class RunuserUpdateView(UpdateView, FormView):
    model = models.RunUser
    template_name = 'task/runuser-form.html'
    form_class = forms.RunUserForm
    success_url = reverse_lazy('host:runuser-list')


class RunUserDeleteView(DeleteView):
    model = models.RunUser
    success_url = reverse_lazy('host:runuser-list')
