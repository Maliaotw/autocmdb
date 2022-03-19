from django.forms import ModelForm
from django import forms
from . import models


class VMForm(ModelForm):
    num_cpus_choice = ((1, '1'), (2, '2'), (4, '4'), (8, '8'))
    num_cpus = forms.ChoiceField(label='CPU (個)', choices=num_cpus_choice)
    memory_choice = ((1024, '1G'), (2048, '2G'), (4096, '4G'), (8192, '8G'), (16384, '16G'), (32768, '32G'))
    memory_mb = forms.ChoiceField(label='內存', choices=memory_choice)
    size_choice = ((50, '50G'), (100, '100G'), (500, '500G'), (1000, '1T'), (2000, '2T'))
    size_gb = forms.ChoiceField(label='硬盤', choices=size_choice)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = models.VM
        fields = '__all__'
        exclude = ['instance', 'check', 'task', 'status', 'is_finish', 'manage_ip']
