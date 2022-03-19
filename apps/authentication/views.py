# ~*~ coding: utf-8 ~*~
#

from __future__ import unicode_literals
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import reverse, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from .signals import post_auth_failed, post_auth_success
from . import forms
from django.contrib.auth.models import User
from .models import UserLoginLog as LoginLog
from django.views.generic import ListView
from . import models
from django.db.models import Q
import logging
from . import signals_handlers
from . import filters

logger = logging.getLogger(__name__)

__all__ = [
    'UserLoginView', 'UserLogoutView'
]


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class UserLoginView(FormView):
    form_class = forms.UserLoginForm
    redirect_field_name = 'next'
    key_prefix_captcha = "_LOGIN_INVALID_{}"
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        logger.info(request.GET.urlencode())
        # print('danisijdidasijs')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        user = form.get_user()
        auth_login(self.request, user)
        self.send_auth_signal(success=True, user=user)
        return redirect(self.request.GET.get('next', '/'))

    def form_invalid(self, form):
        # write login failed log
        username = form.cleaned_data.get('username')
        exist = User.objects.filter(username=username).first()
        # 如果有帳戶 為密碼錯 , 如無帳戶為帳密錯
        reason = LoginLog.REASON_PASSWORD if exist else LoginLog.REASON_NOT_EXIST
        # limit user login failed count
        # ip = get_request_ip(self.request)
        self.send_auth_signal(success=False, username=username, reason=reason)

        form._errors = form.errors
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def send_auth_signal(self, success=True, user=None, username='', reason=''):
        if success:
            logger.info('success')
            # post_auth_success.send(sender=self.__class__, user=user, request=self.request)
            signals_handlers.on_user_auth_success(sender=self.__class__, user=user, request=self.request)
        else:
            logger.warning('fail')
            # post_auth_failed.send(
            #     sender=self.__class__, username=username,
            #     request=self.request, reason=reason
            # )
            signals_handlers.on_user_auth_failed(
                sender=self.__class__,
                username=username,
                request=self.request, reason=reason
            )


@method_decorator(never_cache, name='dispatch')
class UserLogoutView(TemplateView):
    # template_name = ''

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        # next_uri = request.COOKIES.get("next")
        # if next_uri:
        #     return redirect(next_uri)
        # response = super().get(request, *args, **kwargs)
        # return response

        return redirect('/login')

    def get_context_data(self, **kwargs):
        # context = {
        #     'title': _('Logout success'),
        #     'messages': _('Logout success, return login page'),
        #     'interval': 1,
        #     'redirect_url': reverse('authentication:login'),
        #     'auto_redirect': True,
        # }
        # kwargs.update(context)
        return super().get_context_data(**kwargs)


# 審計


from django.utils import timezone


class DatetimeSearchMixin:
    date_format = '%Y-%m-%d'
    date_from = date_to = None

    def get_date_range(self):
        date_from_s = self.request.GET.get('date_from')
        date_to_s = self.request.GET.get('date_to')

        if date_from_s:
            date_from = timezone.datetime.strptime(date_from_s, self.date_format)
            tz = timezone.get_current_timezone()
            self.date_from = tz.localize(date_from)
        else:
            self.date_from = timezone.now() - timezone.timedelta(7)

        if date_to_s:
            date_to = timezone.datetime.strptime(
                date_to_s + ' 23:59:59', self.date_format + ' %H:%M:%S'
            )
            self.date_to = date_to.replace(
                tzinfo=timezone.get_current_timezone()
            )
        else:
            self.date_to = timezone.now()

    def get(self, request, *args, **kwargs):
        self.get_date_range()
        return super().get(request, *args, **kwargs)


class LoginListView(DatetimeSearchMixin, ListView):
    model = models.UserLoginLog
    template_name = 'audits/login_list.html'
    paginate_by = 10
    user = keyword = ""
    date_to = date_from = None

    def param_replace(self):
        # 支持分頁器
        data = self.request.GET.copy()
        if self.page_kwarg in data.keys():
            data.pop(self.page_kwarg)

        return {k: v for k, v in data.items() if v}

    def get_queryset(self):

        queryset = super().get_queryset()

        self.user = self.request.GET.get('username', '')
        self.keyword = self.request.GET.get("keyword", '')

        queryset = queryset.filter(
            datetime__gt=self.date_from, datetime__lt=self.date_to
        )
        if self.user:
            queryset = queryset.filter(username=self.user)
        if self.keyword:
            queryset = queryset.filter(
                Q(ip__contains=self.keyword) |
                Q(city__contains=self.keyword) |
                Q(username__contains=self.keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):

        context = {}

        context.update({
            'app': _('Audits'),
            'action': _('Login log'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            'keyword': self.keyword,
            'userlist': User.objects.values_list('id', 'username')
        })
        context['search_field'] = self.param_replace()
        # print(context)
        if self.request.GET.get('contacts'):
            self.paginate_by = int(self.request.GET.get('contacts', 10))

        context.update({
            'page_list': [10, 20, 50, 100]
        })

        kwargs.update(context)
        return super().get_context_data(**kwargs)
