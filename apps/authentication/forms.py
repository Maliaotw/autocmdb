# -*- coding: utf-8 -*-
#

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Username'), max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "帳戶"}))
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "密碼"}),
        max_length=128, strip=False
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct username and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive', )
