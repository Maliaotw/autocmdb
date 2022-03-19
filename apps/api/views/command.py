# -*- coding: utf-8 -*-

import datetime
import logging
import uuid

from django.conf import settings
from rest_framework import generics, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api import serializers
from host import models as host_models
from src.base.permissions import WithBootstrapToken
from src.redisbase import RedisQueue

logger = logging.getLogger(__name__)


class CommandViewSet(GenericViewSet, mixins.RetrieveModelMixin ,generics.ListAPIView):
    permission_classes = [IsAuthenticated | WithBootstrapToken]

    def list(self, request, *args, **kwargs):
        return Response({'data': uuid.uuid4()})

    def create(self, request):
        # logger.info(request.POST)
        from src import ansiblerunner

        if self.request.user.is_anonymous:
            return Response('匿名用戶無法操作命令')


        hostids = request.POST.getlist('hostids[]')
        command = request.POST.get('command')
        request.session['cmd'] = command
        uuid = request.POST.get('uuid')
        runuser = request.POST.get('runuser')

        runuser_obj = host_models.RunUser.objects.get(id=int(runuser))
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

    def retrieve(self, request, *args, **kwargs):
        self.queryset = host_models.CmdRecord.objects.all()
        self.serializer_class = serializers.CmdRecordSerializer
        return super(CommandViewSet, self).retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def node(self, request, *args, **kwargs):
        self.queryset = host_models.Node.objects.all()
        self.serializer_class = serializers.NodeSerializer
        return super(CommandViewSet, self).list(request, *args, **kwargs)


    @action(methods=['get'], detail=False)
    def host(self, request, *args, **kwargs):
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

    @action(methods=['post'], detail=False)
    def shell(self, request, *args, **kwargs):
        import subprocess

        command = request.data.get("cmd")

        return Response(subprocess.getoutput(command))


