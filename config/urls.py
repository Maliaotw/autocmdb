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

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from django.views.static import serve

from authentication.views import UserLoginView, UserLogoutView
from .views import DashBoardView, DashAssetView, DashRackView

urlpatterns = [

    path('admin/', admin.site.urls),

    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', UserLogoutView.as_view(), name="logout"),
    path('', login_required(DashBoardView.as_view()), name='dashboard'),
    path('dashasset', login_required(DashAssetView.as_view()), name='dashasset'),
    path('dashrack', login_required(DashRackView.as_view()), name='dashrack'),
    path('cmdb/', include('host.urls', namespace='host')),
    path('cmdb/', include('authentication.urls', namespace='auth')),
    path('cmdb/', include('asset.urls', namespace='asset')),
    path('cmdb/', include('vm.urls', namespace='vm')),
    path('cmdb/settings/', include('settings.urls.view_urls', namespace='settings')),
    path('api/', include('api.urls', namespace='api')),

    re_path('^media/pems/(?P<path>.*)$', login_required(serve), {"document_root": settings.MEDIA_ROOT}, name='pems'),
]
