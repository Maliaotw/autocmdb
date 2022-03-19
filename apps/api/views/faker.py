import logging
import secrets

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from asset.views import idracCreateView,NetWareCreateView
from host import tasks
logger = logging.getLogger(__name__)
from faker import Faker
import secrets
from rest_framework.permissions import IsAuthenticated
from src.base.permissions import WithBootstrapToken


class FakerViewSet(ViewSet):
    permission_classes = [IsAuthenticated | WithBootstrapToken]

    fake = Faker()

    def list(self, request, *args, **kwargs):
        ret = {'code': '0', 'data': [], 'message': f'healthz Hello {request.user}'}
        return Response(ret)

    @action(methods=['post'], detail=False)
    def idrac(self, request: Request, *args, **kwargs):
        self.request._request.POST._mutable = True
        self.request._request.POST['idrac_ip'] = self.fake.ipv4_private()
        self.request._request.POST['port'] = 22
        self.request._request.POST['user'] = 'cmdb'
        self.request._request.POST['passwd'] = secrets.token_hex(4)

        _idrac_obj = idracCreateView()
        _idrac_obj.request = self.request._request
        _idrac_obj.post(self.request._request, *args, **kwargs)

        tasks.idracinfo(iid=_idrac_obj.object.id)

        return Response(f'新增成功 {str(_idrac_obj.object)}')

    @action(methods=['post'], detail=False)
    def netware(self,request: Request, *args, **kwargs):
        from src.demo.netware import Netware

        self.request._request.POST._mutable = True
        self.request._request.POST = Netware().data

        _obj = NetWareCreateView()
        _obj.request = self.request._request
        _obj.post(self.request._request, *args, **kwargs)

        return Response(f'新增成功 {str(_obj.object)}')
