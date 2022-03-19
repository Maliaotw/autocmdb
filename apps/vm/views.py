from django.shortcuts import render
from django.views.generic import ListView, CreateView
from . import models
from . import forms
# from dwebsocket.decorators import accept_websocket, require_websocket
from django.http import HttpResponse
from django.core.cache import cache
from django.urls import reverse_lazy
from src.ansiblerunner import PlayBookRunner
from . import tasks
import json
import time
from celery.result import AsyncResult
from . import filters
from src.base.views import FilteredListView

# Create your views here.

class VMListView(FilteredListView):
    model = models.VM
    paginate_by = 10
    filterset_class = filters.VMFilter
    template_name = 'vm/vm-list.html'

    # def get_context_data(self):
    #     if self.request.GET.get('contacts'):
    #         self.paginate_by = int(self.request.GET.get('contacts', 10))
    #     context = super().get_context_data()
    #     context.update({
    #         'page_list': [10, 20, 50, 100]
    #     })
    #     # print(context)
    #     return context





class VMCreateView(CreateView):
    model = models.VM
    paginate_by = 10
    template_name = 'vm/vm_form.html'
    form_class = forms.VMForm
    success_url = reverse_lazy("vm:vm-list")

    def form_invalid(self, form):
        return super(VMCreateView, self).form_invalid(form)

    def form_valid(self, form):
        '''
        成功create 發信號
        {'name': 'demo-web3', 'num_cpus': 1, 'memory_mb': 1024, 'size_gb': 20}
        '''
        data = form.cleaned_data
        cache.set(data['name'], data)  # 放緩存 發信號
        obj = super().form_valid(form)
        return obj

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# @accept_websocket
# def echo_once(request):
#     if not request.is_websocket():  # 判断是不是websocket连接
#         return HttpResponse('message')
#     else:
#         while True:
#             time.sleep(1)
#             for vm in models.VM.objects.filter(is_finish=False):
#
#                 # print(vm)
#                 data = cache.get(vm.name)
#                 # print(data)
#                 if data:
#                     check = data.get('check')
#                     if check:
#                         vm.check = check
#
#                     manage_ip = data.get('manage_ip')
#                     if manage_ip:
#                         vm.manage_ip = manage_ip
#
#                     task = data.get('task')
#                     t = AsyncResult(task)
#                     if t.status == 'FAILURE':
#                         vm.check = '即將銷毀'
#                         vm.is_finish = True
#                         vm.status = 5
#                         data.update({'check':'即將銷毀...','status':'構建失敗'})
#                         cache.set(vm.name,data)
#
#                     if data.get('is_finish'):
#                         vm.is_finish = True
#                         vm.status = 1
#
#                     vm.save()
#
#                     request.websocket.send(json.dumps(data))
#