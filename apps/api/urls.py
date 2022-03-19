from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls import url
from rest_framework import routers

from .views import HealthzViewSet, FakerViewSet, IdracViewSet, CommandViewSet, TaskResultViewSet,AssetsViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('healthz', HealthzViewSet, 'healthz')
router.register('faker', FakerViewSet, 'faker')
router.register('idrac', IdracViewSet, 'idrac')
router.register('command', CommandViewSet, 'command')
router.register('taskresult', TaskResultViewSet, 'taskresult')
router.register('assets', AssetsViewSet, 'assets')

urlpatterns = [

]

urlpatterns += router.urls
