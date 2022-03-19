from django.forms import ModelForm
from . import models
# from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import generic_inlineformset_factory, modelformset_factory
from host import models as host_models
from django import forms

class AssetForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.Asset
        fields = '__all__'
        exclude = ['content_type', 'object_id','name']


class IDCForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.IDC
        fields = '__all__'


class RackForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.Rack
        fields = '__all__'

class RackUnitForm(ModelForm):

    class Meta:
        model = models.RackUnit
        fields = '__all__'



class IdracForm(ModelForm):
    '''
    IDRAC創建表單
    '''


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = host_models.idrac
        fields = '__all__'
        exclude = ['host','task']
        widgets = {
            'passwd': forms.TextInput(attrs={
                'class':'form-control','type':'password'
            }),

        }



class TagForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.Tag
        fields = '__all__'




class NetWareFrom(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.NetworkDevice
        fields = '__all__'


class ISPFrom(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.ISP
        fields = '__all__'