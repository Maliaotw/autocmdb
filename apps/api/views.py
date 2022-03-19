# -*- coding: utf-8 -*-

from asset import models as asset_models
from host import models as host_models
from django.http import HttpResponse
from django_celery_results import models as dcr_models
from api import serializers
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from host import tasks
from ast import literal_eval
import uuid
from .tasks import ansible
from django.core.cache import cache
from src.redisbase import RedisQueue
import datetime
from rest_framework import permissions
import pytz
import time
import hashlib
from django.conf import settings
import logging
import ast

logger = logging.getLogger(__name__)

auth_list = []

from django.shortcuts import render
# from apps.app import models
# from apps.app import serializers

from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView, Response
from rest_framework import status


class AssetData(APIView):
    permission_classes = (permissions.AllowAny,)
    ck = "mdfmsijfiosdjoidfjdf"

    def set_mem(self, h_obj, data):
        # models.Memory.objects.filter(slot="", manufacturer="", capacity="", host_obj="", model="", sn="")
        in_host = host_models.Memory.objects.filter(host_obj=h_obj)

        summary = []

        for i in data:
            if in_host.filter(slot=i['slot']):
                # 已存在 看差異
                if in_host.filter(manufacturer=i['manufacturer'], capacity=i['capacity'], slot=i['slot']):
                    logger.info("沒有變化")
                    # summary.append("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(slot=i['slot']).update(manufacturer=i['manufacturer'], capacity=i['capacity'])
                    summary.append("更新 %s %s" % (i['slot'], i['size']))

            else:
                logger.info("新增內存")
                host_models.Memory.objects.create(
                    manufacturer=i['manufacturer'],
                    capacity=i['capacity'],
                    slot=i['slot'],
                    host_obj=h_obj,
                    model=i['model'],
                    sn=i['sn']
                )
                summary.append("新增 %s %s" % (i['slot'], i['capacity']))

        if summary:
            summary.insert(0, "內存:")

        return summary

    def set_nic(self, h_obj, data):
        summary = []

        for i in data:
            # models.NIC.objects.filter(macaddress="", model="", netmask="", ipaddress="", name='')
            in_host = host_models.NIC.objects.filter(host_obj=h_obj)

            if in_host.filter(name=i['name']):
                # 已存在
                if in_host.filter(macaddress=i['macaddress'], ipaddress=i['ipaddress'], name=i['name']):
                    logger.info("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(name=i['name']).update(
                        macaddress=i['macaddress'],
                        ipaddress=i['ipaddress'],
                        netmask=i['netmask'],
                        model=i['model']
                    )
                    summary.append("更新 %s %s" % (i['name'], i['ipaddress']))
            else:
                logger.info("新增網卡")
                host_models.NIC.objects.create(
                    macaddress=i['macaddress'],
                    model=i['model'],
                    netmask=i['netmask'],
                    ipaddress=i['ipaddress'],
                    name=i['name'],
                    host_obj=h_obj
                )
                summary.append("新增 %s %s" % (i['name'], i['ipaddress']))

        if summary:
            summary.insert(0, "網卡:")

        return summary

    def set_disk(self, h_obj, data):
        summary = []

        for i in data:
            # models.Disk.objects.filter(slot="", model="", capacity="", host_obj="", sn="", manufacturer="", iface_type="")
            in_host = host_models.Disk.objects.filter(host_obj=h_obj)

            if in_host.filter(slot=i['slot']):
                # 已存在
                if in_host.filter(capacity=i['capacity'], slot=i['slot'], model=i['model']):
                    logger.info("沒有變化")
                    # summary.append("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(slot=i['slot']).update(
                        capacity=i['capacity'],
                        slot=i['slot'],
                        model=i['model'],
                        sn=i['sn'],
                        manufacturer=i['manufacturer'],
                        iface_type=i['iface_type']
                    )
                    summary.append("更新 %s %s" % (i['slot'], i['capacity']))
            else:
                logger.info("新增硬盤")
                host_models.Disk.objects.create(
                    slot=i['slot'],
                    model=i['model'],
                    capacity=i['capacity'],
                    host_obj=h_obj,
                    sn=i['sn'],
                    manufacturer=i['manufacturer'],
                    iface_type=i['iface_type']
                )
                summary.append("新增 %s %s" % (i['slot'], i['capacity']))

        if summary:
            summary.insert(0, "硬盤:")

        return summary

    def set_cpu(self, h_obj, data):
        summary = []

        for i in data:
            # models.CPU.objects.filter(slot="",manufacturer="",model="",cores="",threads="",host_obj="")
            in_host = host_models.CPU.objects.filter(host_obj=h_obj)

            if in_host.filter(slot=i['slot']):
                # 已存在
                if in_host.filter(slot=i['slot'], model=i['cpu_model']):
                    logger.info("沒有變化")
                else:
                    in_host.filter(slot=i['slot']).update(
                        manufacturer=i['manufacturer'],
                        model=i['model'],
                        cores=i['cores'],
                        threads=i['threads']
                    )
                    summary.append("更新 %s %s" % (i['slot'], i['cores']))
            else:
                logger.info("新增CPU")
                host_models.CPU.objects.create(
                    slot=i['slot'],
                    manufacturer=i['manufacturer'],
                    model=i['model'],
                    cores=i['cores'],
                    host_obj=h_obj
                )
                summary.append("新增 %s %s" % (i['slot'], i['cores']))

        if summary:
            summary.insert(0, "CPU:")

        return summary

    def run(self, data):

        basic = data['basic']
        logger.info(f'basic {basic}')

        record = {'title': '', 'summary': []}

        node, created = host_models.Node.objects.get_or_create(name="-".join(basic['name'].split("-")[:-1]))

        remote_addr = self.request._request.META['REMOTE_ADDR']

        h_obj, created = host_models.Host.objects.get_or_create(
            name=basic['name'],
            sn=basic['sn'],
            node=node,
            cate=2,
            defaults={
                'manage_ip': basic['manage_ip'],
                'manage_ssh': basic['manage_ssh'],
                'model': basic['model'],
                'manufacturer': basic['manufacturer'],
                'os_platform': basic['os_platform'],
                'os_distribution': basic['os_distribution'],
                'os_version': basic['os_version'],
                'total_memory': sum([i['capacity'] for i in data['mem']]),
                'total_disk': sum([i['capacity'] for i in data['disk']]),
                'total_cores': sum([int(i['cores']) for i in data['cpu']]),
            }
        )
        if created:
            record['title'] = 'ADD %s' % h_obj.name

        # proc

        proclist = data.get('proc')
        hp = host_models.HostProc.objects.create(host=h_obj)
        for i in proclist:
            i['create_time'] = datetime.datetime.fromtimestamp(i['create_time']).replace(tzinfo=pytz.utc)
            proc_obj = host_models.Process.objects.create(**i)
            hp.proc.add(proc_obj)
        hp.save()

        # net
        netlist = data.get('net')
        hn = host_models.HostNet.objects.create(host=h_obj)
        for i in netlist:
            net_obj = host_models.Net.objects.create(**i)
            hn.net.add(net_obj)
        hn.save()

        record['summary'] += self.set_mem(h_obj, data['mem'])
        record['summary'] += self.set_nic(h_obj, data['nic'])
        record['summary'] += self.set_disk(h_obj, data['disk'])
        record['summary'] += self.set_cpu(h_obj, data['cpu'])

        if record['summary'] and not record['title']:
            record['title'] = '更新 %s' % h_obj.name
            ret = "Update %s" % h_obj.name

        if record['title']:
            # 建立資產變更紀錄表
            record['summary'] = "\n".join(record['summary'])
            host_models.HostRecord.objects.create(host_obj=h_obj, **record)
        else:
            record['title'] = 'Noting'

        return record['title']

    def post(self, request):

        # logger.info(request.META)

        if settings.ENV_MODE == 'DEMO':
            from src.demo.instances import INSTANCE
            data = INSTANCE().data
            ret = self.run(data)
            return Response({'data': ret})

        response = 500
        auth_key_time = self.request._request.META["HTTP_AUTH_KEY"]

        auth_key_client, client_ctime = auth_key_time.split("|")
        server_current_time = time.time()
        if server_current_time - 30 > float(client_ctime):
            # 太久遠
            msg = "驗證失敗"
        if auth_key_time in auth_list:
            # 已經訪問過
            msg = "你來晚了"

        # 開始驗證
        key_time = "%s|%s" % (self.ck, client_ctime)
        m = hashlib.md5()
        m.update(bytes(key_time, encoding='utf-8'))
        authkey = m.hexdigest()

        if authkey != auth_key_client:
            msg = "授權失敗"
        else:
            response = 200

        if response != 200:
            return Response({"msg": msg})

        auth_list.append(auth_key_time)
        # logger.info(request)
        # self.request
        data = ast.literal_eval(request.data)
        ret = self.run(data)

        return Response({'data': ret})


def api_refresh_asset(request):
    '''
    idrac 更新硬件信息
    :param request:
    :return:
    '''
    id = request.GET.get('id')
    ret = tasks.idracinfo(iid=id)

    return HttpResponse('ok')


def command_executions(request):
    logger.info(request.POST)
    return HttpResponse('ok')


class TaskLogApiView(APIView):
    def get(self, request):

        '''
        TODO  修改為websocket
        :param request:
        :return:
        '''
        if settings.ENV_MODE == 'DEMO':
            return Response({'end': True, 'data': 'DEMO環境無法進行命令'})

        uuid = request.GET.get('uuid')
        self.rq = RedisQueue(uuid)
        data = {}
        ret = self.rq.get(timeout=1)
        if not ret:
            ret = ''
        # cache.set(uuid,'')
        # # logger.info(ret)
        if 'end' in ret:
            data['end'] = True
            data['data'] = ret
        else:
            data['data'] = ret
        return Response(data)


class CommandApiView(APIView):

    def get(self, request):
        return Response({'data': uuid.uuid4()})

    def post(self, request):
        # logger.info(request.POST)
        from src import ansiblerunner

        hostids = request.POST.getlist('hostids[]')
        command = request.POST.get('command')
        request.session['cmd'] = command
        uuid = request.POST.get('uuid')
        runuser = request.POST.get('runuser')

        runuser_obj = host_models.RunUser.objects.get(id=runuser)
        private_key = runuser_obj.private_key.file or runuser_obj.password
        host_data = []
        host_objs = []
        for id in hostids:
            host_obj = host_models.Host.objects.get(id=id)
            host_objs.append(host_obj)
            # logger.info(host_obj)
            # logger.info(host_obj.manage_ip)
            data = {
                "hostname": host_obj.name,
                "ip": host_obj.manage_ip,
                "port": host_obj.manage_ssh,
                "username": runuser_obj.username,
                "private_key": private_key
            }
            host_data.append(data)

        inventory = ansiblerunner.BaseInventory(host_data)
        runner = ansiblerunner.CommandRunner(inventory)
        # tasks = [
        #     {"action": {"module": "ping", "data": "pong"}, "name": "check connect to host"},
        # ]

        # TODO try

        date_start = datetime.datetime.now()
        # result = runner.run(tasks=tasks, pattern='all',uuid=uuid)
        if settings.ENV_MODE == 'DEMO':
            log = ['DEMO環境無法進行命令']
        else:
            result = runner.execute(cmd=command, pattern='all', uuid=uuid)
            log = result.log
        # logger.info(result.log)
        date_finished = datetime.datetime.now()

        # 保存命令歷史
        cr_obj = host_models.CmdRecord(
            user=self.request.user,
            command=command,
            _result="".join(log),
            is_finished=True,
            date_start=date_start,
            date_finished=date_finished

        )
        cr_obj.save()

        for h in host_objs:
            cr_obj.host.add(h)

        if settings.ENV_MODE != 'DEMO':
            rq = RedisQueue(uuid)
            rq.put('end')

        return Response({'data': 'success'})


class CmdResultApi(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = host_models.CmdRecord.objects.all()
    serializer_class = serializers.CmdRecordSerializer


class TaskResultApi(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = dcr_models.TaskResult.objects.all()
    serializer_class = serializers.TaskResultSerializer

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        import time
        time.sleep(2)
        # t = run_ansible_task.delay(str(task.id))
        if task.status == 'FAILURE':
            task.result = task.traceback
        else:
            task.result = literal_eval(task.result)['data']

        # return super().retrieve(request, *args, **kwargs)
        return Response({'id': task.id, 'status': task.status, 'result': task.result})


class HostListApi(APIView):

    def get(self, req):
        objs = host_models.Node.objects.all()
        ret = []
        for node in objs:

            data = {'id': node.id, 'name': "%s (%s)" % (node.name, node.host_set.all().count()), 'pId': 0}
            ret.append(data)
            for host in node.host_set.all():
                data = {
                    'id': host.id + 10000,
                    'name': host.name,
                    'pId': node.id,
                    'hostid': host.id,
                    'iconClass': 'fa fa-pen'
                }
                ret.append(data)

        return Response(ret)


class NodeListApi(generics.ListAPIView):
    queryset = host_models.Node.objects.all()
    serializer_class = serializers.NodeSerializer
