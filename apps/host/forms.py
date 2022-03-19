from django.forms import ModelForm
from . import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import generic_inlineformset_factory,modelformset_factory


class HostForm(ModelForm):
    """主機表單"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.Host
        fields = '__all__'


class NICForm(ModelForm):
    """網卡表單"""
    def __init__(self, *args, **kwargs):
        super(NICForm, self).__init__(*args, **kwargs)
        # 對所有字段添加Css屬性
        for k, v in self.fields.items():

            self.fields[k].widget.attrs['class'] = 'form-control'
            self.fields[k].widget.attrs['disabled'] = 'ture'


    class Meta:
        model = models.NIC
        fields = '__all__'



class DiskForm(ModelForm):
    """硬盤表單"""

    def __init__(self, *args, **kwargs):
        super(DiskForm, self).__init__(*args, **kwargs)
        # 對所有字段添加Css屬性

        for k, v in self.fields.items():

            self.fields[k].widget.attrs['class'] = 'form-control'
            self.fields[k].widget.attrs['disabled'] = 'ture'

    class Meta:
        model = models.Disk
        fields = '__all__'


class MemoryForm(ModelForm):
    """硬盤表單"""

    def __init__(self, *args, **kwargs):
        super(MemoryForm, self).__init__(*args, **kwargs)
        # 對所有字段添加Css屬性
        for k, v in self.fields.items():

            self.fields[k].widget.attrs['class'] = 'form-control'
            self.fields[k].widget.attrs['readonly'] = 'ture'

    class Meta:
        model = models.Memory
        fields = '__all__'




class BusUnitFrom(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.BusinessUnit
        fields = '__all__'



class RunUserForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = models.RunUser
        fields = '__all__'







