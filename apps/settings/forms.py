# -*- coding: utf-8 -*-
#
import json
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db import transaction

from .models import Setting, settings
from common.fields import (
    FormDictField, FormEncryptCharField, FormEncryptMixin
)


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            value = getattr(settings, name, None)
            db_setting = Setting.objects.filter(name=name).first()


            if db_setting:
                initial_value = db_setting.value
            elif value is not None:
                if isinstance(value, dict):
                    value = json.dumps(value)
                initial_value = value
            else:
                initial_value = ''
            field.initial = initial_value

    def save(self, category="default"):
        if not self.is_bound:
            raise ValueError("Form is not bound")

        # db_settings = Setting.objects.all()
        if not self.is_valid():
            raise ValueError(self.errors)

        with transaction.atomic():
            for name, value in self.cleaned_data.items():
                field = self.fields[name]
                if isinstance(field.widget, forms.PasswordInput) and not value:
                    continue
                # if value == getattr(settings, name):
                #     continue

                encrypted = True if isinstance(field, FormEncryptMixin) else False
                try:
                    setting = Setting.objects.get(name=name)
                except Setting.DoesNotExist:
                    setting = Setting()
                setting.name = name
                setting.category = category
                setting.encrypted = encrypted
                setting.value = value
                setting.save()


class IDRACSettingForm(BaseForm):

    IDRAC_USER = forms.CharField(
        max_length=1024, label=_("IDRAC_USER"), initial=''
    )

    IDRAC_PASSWD = forms.CharField(
        max_length=1024, label=_("IDRAC_PASSWD"), initial=''
    )


class VcenterSettingForm(BaseForm):

    VCENTER_SERVER = forms.CharField(
        max_length=1024, label=_("VCENTER_SERVER"), initial=''
    )

    VCENTER_USER = forms.CharField(
        max_length=1024, label=_("VCENTER_USER"), initial=''
    )

    VCENTER_PASS = forms.CharField(
        max_length=1024, label=_("VCENTER_PASS"), initial=''
    )


class AsnibleSettingForm(BaseForm):

    MANAGE_USER = forms.CharField(
        max_length=1024, label=_("MANAGE_USER"), initial=''
    )

    MANAGE_PASSWD = forms.CharField(
        max_length=1024, label=_("MANAGE_PASSWD"), initial=''
    )
