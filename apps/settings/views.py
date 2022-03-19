from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.core.exceptions import ImproperlyConfigured

from .forms import AsnibleSettingForm, VcenterSettingForm, IDRACSettingForm

import logging

logger = logging.getLogger(__name__)


class SettingView(TemplateView):
    form_class = ''
    template_name = ""
    success_url = reverse_lazy('')

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Settings'),
            'action': _('Basic setting'),
            'form': self.form_class(),
        }
        kwargs.update(context)
        r = super().get_context_data(**kwargs)
        return r

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            msg = _("Update setting successfully")
            messages.success(request, msg)
            return redirect(self.get_success_url())
        else:
            context = self.get_context_data()
            context.update({"form": form})
            return render(request, self.template_name, context)


class IdracSettingView(SettingView):
    form_class = IDRACSettingForm
    template_name = "settings/basic_setting.html"
    success_url = reverse_lazy('settings:iDRAC-setting')

    def get_context_data(self, **kwargs):
        context = {
            'message': 'iDRAC默認帳號, 用於採集硬件參數'
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VcenterSettingView(SettingView):
    form_class = VcenterSettingForm
    template_name = "settings/basic_setting.html"
    success_url = reverse_lazy('settings:vcenter-setting')

    def get_context_data(self, **kwargs):
        context = {
            'message': 'VCENTER連接參數, 用於創建虛擬機'
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AnsibleSettingView(SettingView):
    form_class = AsnibleSettingForm
    template_name = "settings/basic_setting.html"
    success_url = reverse_lazy('settings:ansible-setting')

    def get_context_data(self, **kwargs):
        context = {
            'message': '虛擬機模板創建後默認帳號, 用於Ansible自動初始化虛擬機'
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
