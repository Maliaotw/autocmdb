from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from .views import LoginListView

app_name = 'authentication'

urlpatterns = [
    # cmdrecord
    url(r'^logs/$', login_required(LoginListView.as_view()), name='login-list'),

]
