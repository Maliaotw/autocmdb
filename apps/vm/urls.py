from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from .views import *

app_name = 'vm'

urlpatterns = [
    # vm
    url(r'^vm/$', login_required(VMListView.as_view()), name='vm-list'),
    url(r'^vm/create$', login_required(VMCreateView.as_view()), name='vm-create'),

    # url(r'^vm/echo_once/$', echo_once),

]



