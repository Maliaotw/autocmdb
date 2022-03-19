from __future__ import absolute_import

from django.conf.urls import url
from django.urls import path

from .. import views

from django.contrib.auth.decorators import login_required, permission_required

app_name = 'settings'

urlpatterns = [
    path('iDRAC', login_required(views.IdracSettingView.as_view()), name='iDRAC-setting'),
    path('vcenter', login_required(views.VcenterSettingView.as_view()), name='vcenter-setting'),
    path('ansible', login_required(views.AnsibleSettingView.as_view()), name='ansible-setting'),

]
