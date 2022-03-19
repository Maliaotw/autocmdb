from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from .views import *

app_name = 'asset'

urlpatterns = [

    # Asset
    url(r'^asset$', login_required(AssetListView.as_view()), name='asset-list'),
    url(r'^asset/(?P<pk>[0-9]+)/update$', login_required(AssetUpdateView.as_view()), name='asset-update'),

    # Server IDRAC
    url(r'^idrac/$', login_required(idracListView.as_view()), name='idrac-list'),
    url(r'^idrac/create$', login_required(idracCreateView.as_view()), name='idrac-create'),
    url(r'^idrac/(?P<pk>[0-9]+)/detail$', login_required(idracDetailView.as_view()), name='idrac-datail'),
    url(r'^idrac/(?P<pk>[0-9]+)/delete$', login_required(idracDeleteView.as_view()), name='idrac-delete'),

    # IDC
    url(r'^idc/$', login_required(IDCListView.as_view()), name='idc-list'),
    url(r'^idc/create$', login_required(IDCCreateView.as_view()), name='idc-create'),
    url(r'^idc/(?P<pk>[0-9]+)/update$', login_required(IDCUpdateView.as_view()), name='idc-update'),
    url(r'^idc/(?P<pk>[0-9]+)/delete$', login_required(IDCDeleteView.as_view()), name='idc-delete'),

    # TAG
    url(r'^tag/$', login_required(TagListView.as_view()), name='tag-list'),
    url(r'^tag/create$', login_required(TagCreateView.as_view()), name='tag-create'),
    url(r'^tag/(?P<pk>[0-9]+)/update$', login_required(TagUpdateView.as_view()), name='tag-update'),
    url(r'^tag/(?P<pk>[0-9]+)/delete$', login_required(TagDeleteView.as_view()), name='tag-delete'),

    # Rack
    url(r'^rack/$', login_required(RackViewList.as_view()), name='rack-list'),
    url(r'^rack/create$', login_required(RackCreateView.as_view()), name='rack-create'),
    url(r'^rack/(?P<pk>[0-9]+)/update$', login_required(RackUpdateView.as_view()), name='rack-update'),
    url(r'^rack/(?P<pk>[0-9]+)/delete$', login_required(RackDeleteView.as_view()), name='rack-delete'),

    # RackUnit
    url(r'^rackunit/$', login_required(RackUnitListView.as_view()), name='rackunit-list'),
    url(r'^rackunit/(?P<pk>[0-9]+)/update$', login_required(RackUnitUpdateView.as_view()), name='rackunit-update'),

    # IDC
    url(r'^isp/$',login_required(ISPListView.as_view()),name='isp_list'),
    url(r'^isp/create$', login_required(ISPCreateView.as_view()), name='isp-create'),
    url(r'^isp/(?P<pk>[0-9]+)/update$', login_required(ISPDetailView.as_view()), name='isp-update'),
    url(r'^isp/(?P<pk>[0-9]+)/delete$', login_required(ISPDeleteView.as_view()), name='isp-delete'),

    # periodictask
    url(r'^pt/$', login_required(PeriodicTaskListView.as_view()), name='pt-list'),

    # taskdetail
    url(r'^td/$', login_required(TaskDetailListView.as_view()), name='td-list'),

    # command
    url(r'^command/$', login_required(CmdListView.as_view()), name='cmd-list'),
    url(r'^command-playbook/$', login_required(CmdPlayListView.as_view()), name='cmd-play-list'),
    # url(r'^command/wsplaybook/$', playbook,name='cmd-ws-play'),


    # net
    url(r'^netware/$', login_required(NetWareListView.as_view()), name='netware-list'),
    url(r'^netware/create$', login_required(NetWareCreateView.as_view()), name='netware-create'),
    url(r'^netware/(?P<pk>[0-9]+)/update$', login_required(NetWareUpdateView.as_view()), name='netware-update'),
    url(r'^netware/(?P<pk>[0-9]+)/delete$', login_required(NetWareDeleteView.as_view()), name='netware-delete'),

]
