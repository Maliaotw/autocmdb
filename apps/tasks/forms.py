from .models import TaskDetail
from djcelery import models as dj_model
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from djcelery import admin as df_admin
import json
import ast


# PeriodicTask = dj_model.PeriodicTask.objects.all()


class DemoForm(ModelForm):
    class Meta:
        model = TaskDetail
        fields = '__all__'


class PTaskForm(ModelForm):
    name = forms.CharField(
        error_messages={
            'invalid': _("名稱不能重複"),
            'required': _("該欄位必填"),
        }
    )
    task = df_admin.TaskChoiceField(
        label=_("任務腳本"),
        error_messages={
            'invalid': _("不能重複"),
            'required': _("該欄位必填"),
        }
    )

    crontab = forms.CharField(
        error_messages={
            'invalid': _("輸入格式不正確"),
            'required': _("該欄位必填"),
        }
    )

    # args = forms.CharField()
    # enabled = forms.BooleanField()

    def clean_task(self):
        """判斷任務腳本是否重複

        :return:
        """
        task = self.cleaned_data.get('task')
        if task == self.instance.task:
            pass
            # print(self.instance.task)
        else:
            if dj_model.PeriodicTask.objects.filter(task=task):
                # print('重複')
                self.add_error('task', '任務腳本： 選擇不能重複')
        # print(self._meta.model)
        # print(task)

        return task

    def clean_args(self):
        """判斷參數格式是否正確"""

        args = self.cleaned_data.get('args')
        # print(args)

        try:
            args = ast.literal_eval(args)
            if isinstance(args, list):
                # print(args)
                # str(args).replace("'",'"')
                return str(args).replace("'",'"')
            else:
                self.add_error('args', '參數： 格式輸入不正確')
                # print('error')
                return args

        except:
            self.add_error('args', '參數： 格式輸入不正確')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # print(name)
        return name

    def clean_crontab(self):
        """判斷日期排程 校對CrontabSchedule表

        :return:
        """
        crontab_mix = self.cleaned_data.get('crontab')
        # print('crontab_mix')
        # print(crontab_mix)
        crontab = crontab_mix.split(' ')
        # print(crontab)
        # x = crontab.pop()
        crontabformat = crontab.pop().replace('(', '').replace(')', '').split('/')
        data = {k: v for k, v in zip(crontabformat, crontab)}
        # print(data)
        #  [{'*/1', 'm'}, {'*', 'h'}, {'*', 'd'}, {'*', 'dM'}, {'*', 'MY'}]
        crontab_obj = dj_model.CrontabSchedule.objects.filter(
            minute=data['m'],
            hour=data['h'],
            day_of_week=data['d'],
            day_of_month=data['dM'],
            month_of_year=data['MY']
        )
        if crontab_obj:
            crontab_obj = crontab_obj.first()
        else:
            crontab_obj = dj_model.CrontabSchedule.objects.create(
                minute=data['m'],
                hour=data['h'],
                day_of_week=data['d'],
                day_of_month=data['dM'],
                month_of_year=data['MY']
            )

        return crontab_obj

    class Meta:
        model = dj_model.PeriodicTask
        fields = '__all__'


class TaskForm(forms.Form):
    name = forms.CharField()
    task = df_admin.TaskChoiceField(label=_('Task (registered)'))
    #
    # task = forms.ModelChoiceField(
    #     label="任務",
    #     queryset=dj_model.PeriodicTask.objects.values_list('task',flat=True),
    #     # to_field_name="name",
    #     widget=forms.Select(attrs={"class": "form-control", "onchange": "get_user_number(this)"}),
    #     required=True,
    #
    # )
    crontab = forms.CharField()
    argval = forms.CharField()
    status = forms.BooleanField()

    def clean_crontab(self):
        crontab_mix = self.cleaned_data.get('crontab')
        # print('crontab_mix')
        # print(crontab_mix)
        crontab = crontab_mix.split(' ')
        # print(crontab)
        # x = crontab.pop()
        crontabformat = crontab.pop().replace('(', '').replace(')', '').split('/')
        data = {k: v for k, v in zip(crontabformat, crontab)}
        # print(data)
        #  [{'*/1', 'm'}, {'*', 'h'}, {'*', 'd'}, {'*', 'dM'}, {'*', 'MY'}]
        crontab_obj = dj_model.CrontabSchedule.objects.filter(
            minute=data['m'],
            hour=data['h'],
            day_of_week=data['d'],
            day_of_month=data['dM'],
            month_of_year=data['MY']
        )
        if crontab_obj:
            crontab_obj = crontab_obj.first()
        else:
            crontab_obj = dj_model.CrontabSchedule.objects.create(
                minute=data['m'],
                hour=data['h'],
                day_of_week=data['d'],
                day_of_month=data['dM'],
                month_of_year=data['MY']
            )

        return crontab_obj
