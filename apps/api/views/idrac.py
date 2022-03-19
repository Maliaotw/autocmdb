# -*- coding: utf-8 -*-

from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.viewsets import GenericViewSet

from host import tasks

from rest_framework.permissions import IsAuthenticated
from src.base.permissions import WithBootstrapToken



# from .tasks import ansible

class IdracViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated | WithBootstrapToken]


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def refresh(self, request, *args, **kwargs):
        """idrac 更新硬件信息

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        _id = request.data.get('id')
        if not _id:
            raise AuthenticationFailed("id未輸入")

        tasks.idracinfo(iid=_id)

        return HttpResponse('ok')
