import logging

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.permissions import IsAuthenticated
from src.base.permissions import WithBootstrapToken

logger = logging.getLogger(__name__)


class HealthzViewSet(ViewSet):
    permission_classes = [IsAuthenticated | WithBootstrapToken]

    def list(self, request, *args, **kwargs):
        ret = {'code': '0', 'data': [], 'message': f'healthz Hello {request.user}'}
        return Response(ret)




