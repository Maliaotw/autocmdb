from django.shortcuts import render, HttpResponse, redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.conf import settings
import redis
# from dwebsocket.decorators import accept_websocket, require_websocket
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView, DetailView
from django.utils import timezone
from django.views.generic.edit import FormMixin
from django.forms.formsets import formset_factory

# Create your views here.
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from . import models
from . import forms
from . import filters
from . import tasks
from host import models as host_models
import json
from django_celery_beat import models as djcelery_model
from django_celery_results import models as dcr_models
from tasks import models as task_model
import ast
from src import ansiblerunner
import datetime
from src.redisbase import RedisQueue
import uuid
from django.core.cache import cache
from django.contrib.sessions.models import Session

from src.base.views import FilteredListView

import logging

logger = logging.getLogger(__name__)


class AssetListView(FilteredListView):
    model = models.Asset
    paginate_by = 10
    filterset_class = filters.AssetListFilter
    template_name = 'basic/asset_list.html'


class AssetUpdateView(UpdateView):
    model = models.Asset
    form_class = forms.AssetForm
    template_name = "basic/asset_update.html"
    success_url = reverse_lazy('asset:asset-list')
    pk_url_kwarg = 'pk'

    def form_invalid(self, form):
        logger.info('form_invalid')
        logger.info(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.info('form_valid')
        return super().form_valid(form)

    def get_idc_data(self):

        data = {}
        for i in models.Rack.objects.all():

            if data.get(i.idc.id):
                data[i.idc.id].append({'name': i.name, 'id': i.id})
            else:
                data[i.idc.id] = [{'name': i.name, 'id': i.id}]

        return data

    def get_context_data(self, **kwargs):
        idc_data = self.get_idc_data()
        context = {
            'idc_data': idc_data,
            'idc_list': models.IDC.objects.all(),
        }

        kwargs.update(context)
        return super().get_context_data(**kwargs)



class idracListView(FilteredListView):
    model = host_models.idrac
    paginate_by = 10
    template_name = 'basic/idrac_list.html'
    filterset_class = filters.IdracListFilter

    def get_queryset(self):
        logger.info(self.request.GET)

        obj = super().get_queryset()

        status = self.request.GET.get('status')
        if status:
            if status == 'false':
                obj = obj.filter(host__isnull=True)
            else:
                obj = obj.filter(host__isnull=False)

        return obj



class idracCreateView(CreateView):
    model = host_models.idrac
    paginate_by = 10
    template_name = 'basic/idrac_form.html'
    form_class = forms.IdracForm
    success_url = reverse_lazy("asset:idrac-list")


class idracDetailView(DetailView, UpdateView):
    model = host_models.idrac
    template_name = 'basic/idrac_detail.html'
    form_class = forms.IdracForm
    success_url = reverse_lazy("asset:idrac-list")
    pk_url_kwarg = 'pk'


class idracDeleteView(DeleteView):
    model = host_models.idrac
    template_name = 'basic/idrac_list.html'
    success_url = reverse_lazy("asset:idrac-list")



class NetWareListView(FilteredListView):
    model = models.NetworkDevice
    paginate_by = 10
    filterset_class = filters.NetworkDeviceFilter
    template_name = 'basic/networkdevice_list.html'


class NetWareCreateView(CreateView):
    model = models.NetworkDevice
    form_class = forms.NetWareFrom
    success_url = reverse_lazy('asset:netware-list')
    template_name = 'basic/networkdevice_form.html'


class NetWareUpdateView(UpdateView):
    model = models.NetworkDevice
    form_class = forms.NetWareFrom
    success_url = reverse_lazy('asset:netware-list')
    template_name = 'basic/networkdevice_form.html'


class NetWareDeleteView(DeleteView):
    model = models.NetworkDevice
    success_url = reverse_lazy('asset:netware-list')


class TagListView(ListView):
    model = models.Tag
    paginate_by = 10
    template_name = 'basic/tag_list.html'


class TagCreateView(CreateView):
    model = models.Tag
    form_class = forms.TagForm
    template_name = 'basic/tag_form.html'
    success_url = reverse_lazy('asset:tag-list')


class TagUpdateView(UpdateView):
    model = models.Tag
    form_class = forms.TagForm
    success_url = reverse_lazy('asset:tag-list')
    template_name = 'basic/tag_form.html'


class TagDeleteView(DeleteView):
    model = models.Tag
    template_name = 'basic/tag_form.html'
    success_url = reverse_lazy('asset:tag-list')


class IDCListView(FilteredListView):
    model = models.IDC
    paginate_by = 10
    template_name = 'idc/idc_list.html'
    filterset_class = filters.IDCListFilter



class IDCCreateView(CreateView):
    model = models.IDC
    form_class = forms.IDCForm
    success_url = reverse_lazy("asset:idc-list")
    template_name = 'idc/idc_form.html'


class IDCUpdateView(UpdateView):
    model = models.IDC
    form_class = forms.IDCForm
    success_url = reverse_lazy("asset:idc-list")
    template_name = 'idc/idc_form.html'


class IDCDeleteView(DeleteView):
    model = models.IDC
    success_url = reverse_lazy("asset:idc-list")


class RackViewList(FilteredListView):
    model = models.Rack
    paginate_by = 10
    template_name = 'idc/rack_list.html'
    filterset_class = filters.RackListFilter



class RackCreateView(CreateView):
    model = models.Rack
    form_class = forms.RackForm
    success_url = reverse_lazy("asset:rack-list")
    template_name = 'idc/rack_form.html'


class RackUpdateView(UpdateView, DetailView):
    model = models.Rack
    form_class = forms.RackForm
    success_url = reverse_lazy("asset:rack-list")
    template_name = 'idc/rack_form.html'

    def post(self, request, *args, **kwargs):
        # print(super().get_form_kwargs())
        # print(self.request.POST)
        obj = super().post(request, *args, **kwargs)
        # print(obj)
        # print(dir(obj))
        # print(obj.status_code)

        # print()
        form = self.get_form()

        if self.request.POST.get('isp'):
            if obj.status_code == 200:
                for i in self.request.POST.get('isp'):
                    self.object.isp.add(models.ISP.objects.get(id=i))

        return obj


class RackDeleteView(DeleteView):
    model = models.Rack
    success_url = reverse_lazy("asset:rack-list")



class RackUnitListView(ListView):
    model = models.RackUnit
    paginate_by = 10
    template_name = 'idc/rackunit_list.html'

    # pk_url_kwarg = 'name'

    def get_queryset(self):
        obj = super().get_queryset()
        name = self.request.GET.get('name')
        self.rack = ''
        self.isp = ''
        if name:
            self.rack = models.Rack.objects.get(id=name)
            self.isp = self.rack.isp.all()
            return obj.filter(name_id=name)
        return obj

    def get_context_data(self, **kwargs):
        hr = list(range(1, self.rack.height + 1))
        hr.reverse()
        # print("kwargs",)
        kwargs = super().get_context_data(**kwargs)

        excludes = []
        for i in kwargs.get('object_list'):
            excludes.append(i.num)
            if i.asset.size > 1 and i.num:
                [excludes.append(i.num - s) for s in range(i.asset.size)]

        # print(kwargs)
        # height = set(hr) - set([i.num for i in kwargs.get('object_list')])
        # print(height)
        content = {
            'rack': self.rack,
            'isps_list': self.isp,
            'height': hr,
            'exclude': excludes
        }
        content.update(kwargs)

        return super().get_context_data(**content)


class RackUnitUpdateView(UpdateView):
    model = models.RackUnit
    template_name = 'idc/rackunit_list.html'
    form_class = forms.RackUnitForm
    success_url = reverse_lazy("asset:rack-list")



class ISPListView(FilteredListView):
    model = models.ISP
    paginate_by = 10
    template_name = 'idc/isp_list.html'
    filterset_class = filters.ISPListFilter


class ISPCreateView(CreateView):
    model = models.ISP
    template_name = 'idc/isp_form.html'
    form_class = forms.ISPFrom
    success_url = reverse_lazy('asset:isp_list')


class ISPDetailView(UpdateView):
    model = models.ISP
    template_name = 'idc/isp_form.html'
    form_class = forms.ISPFrom
    success_url = reverse_lazy('asset:isp_list')


class ISPDeleteView(DeleteView):
    model = models.ISP
    template_name = 'idc/isp_list.html'
    success_url = reverse_lazy('asset:isp_list')



class PeriodicTaskListView(FilteredListView):
    # model = djcelery_model.PeriodicTask
    queryset = djcelery_model.PeriodicTask.objects.filter(task__contains='host')
    paginate_by = 10
    template_name = 'task/PeriodicTask_list.html'
    filterset_class = filters.PeriodicTaskListFilter



class TaskDetailListView(ListView):
    model = task_model.TaskDetail
    template_name = 'task/TaskDetail_list.html'
    paginate_by = 10
    ordering = ['-create_date']

    def get_queryset(self):
        id = self.request.GET.get('id')
        obj = super().get_queryset()

        return obj.filter(name_id=id)

    def get_context_data(self, **kwargs):
        search_field = {}
        id = self.request.GET.get('id')
        search_field['id'] = id

        context = {
            'search_field': search_field,
            'pdtask': djcelery_model.PeriodicTask.objects.get(id=id)

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CmdListView(ListView):
    model = task_model.TaskDetail
    template_name = 'task/command-list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        cmd = self.request.session.get('cmd')
        context = {
            'cmd': cmd,
            'runuserlist': host_models.RunUser.objects.all()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CmdPlayListView(ListView):
    model = task_model.TaskDetail
    template_name = 'task/command-ansible-list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        cmd = self.request.session.get('cmdplay')
        context = {
            'cmd': cmd,
            'runuserlist': host_models.RunUser.objects.all()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


# @accept_websocket
# def playbook(request):
#     # websocket
#
#     if not request.is_websocket():  # 判断是不是websocket连接
#         return HttpResponse('message')
#     else:
#         q = []
#
#         print(request)
#
#         while True:
#             # print('T')
#             for i in q:
#                 # request.websocket.send(i)
#                 # request.websocket.send(json.dumps({'data': str(i)}))
#                 rq = RedisQueue(i)
#                 ret = rq.get(timeout=1)
#                 if not ret:
#                     continue
#
#                 if ret == 'end':
#                     q.remove(i)
#                     continue
#                 request.websocket.send(json.dumps({'data': ret}))
#                 # q = []
#                 # q.append(uuid4)
#
#             if request.websocket.has_messages():
#                 msg = request.websocket.read()
#                 # print(msg)
#                 # print(msg.decode('utf8')) # str
#                 if not msg:
#                     continue
#                 data = ast.literal_eval(msg.decode('utf8'))
#                 if isinstance(data, dict):
#                     # print(data)
#                     # print(type(data))
#                     # 開始執行
#                     hostids = data.get('hostids')
#                     command = data.get('data')
#                     request.session['cmdplay'] = command
#                     request.session.save()
#                     userid = data.get('user')
#                     uuid4 = uuid.uuid4()
#                     t = tasks.pb.delay(hostids,command,uuid4,userid)
#                     # print(t)
#                     q.append(uuid4)


'''
pt.taskdetail_set.all().filter(taskid__status='SUCCESS').count()
pt.taskdetail_set.all().filter(taskid__status='FAILURE').count()

'''
