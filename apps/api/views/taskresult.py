# -*- coding: utf-8 -*-

from ast import literal_eval

from django.conf import settings
from django_celery_results import models as dcr_models
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api import serializers
from src.redisbase import RedisQueue
from rest_framework.permissions import IsAuthenticated
from src.base.permissions import WithBootstrapToken

class TaskResultViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated | WithBootstrapToken]

    def list(self, request, *args, **kwargs):
        """TODO  修改為websocket

        :param request:
        :return:
        """

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

    def retrieve(self, request, *args, **kwargs):
        # lookup_field = 'id'
        self.queryset = dcr_models.TaskResult.objects.all()
        self.serializer_class = serializers.TaskResultSerializer

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
