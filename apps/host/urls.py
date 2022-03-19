"""AutoCmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from .views import *

app_name = 'host'
urlpatterns = [

    url(r'^host/$', login_required(HostListView.as_view()), name='host-list'),
    url(r'^host/(?P<pk>[0-9]+)/detail$', login_required(HostDetailView.as_view()), name='host-datail'),

    url(r'^busunit/$', login_required(BusinessunitListView.as_view()), name='busunit-list'),
    url(r'^busunit/create$', login_required(BusinessunitCreateView.as_view()), name='busunit-create'),
    url(r'^busunit/(?P<pk>[0-9]+)/update$', login_required(BusinessunitUpdateView.as_view()), name='busunit-update'),
    url(r'^busunit/(?P<pk>[0-9]+)/delete$', login_required(BusinessunitDeleteView.as_view()), name='busunit-delete'),

    url(r'^hostrecord/$', login_required(HostRecordListView.as_view()), name='hostrecord-list'),

    url(r'^cmdrecord/$', login_required(CmdRecordLiewView.as_view()), name='cmdrecord-list'),

    url(r'^runuser/$', login_required(RunUserListView.as_view()), name='runuser-list'),
    url(r'^runuser/create$', login_required(RunuserCreateView.as_view()), name='runuser-create'),
    url(r'^runuser/(?P<pk>[0-9]+)/update$', login_required(RunuserUpdateView.as_view()), name='runuser-update'),
    url(r'^runuser/(?P<pk>[0-9]+)/delete$', login_required(RunUserDeleteView.as_view()), name='runuser-delete'),

]
