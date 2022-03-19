from django.contrib import admin
# Register your models here.
# from kombu.transport.django import models as kombu_models

# admin.site.register(kombu_models.Message)

# from djcelery.models import TaskMeta, TaskSetMeta



class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)


from .models import TaskDetail,TaskManualRecord


class TaskDetailAdmin(admin.ModelAdmin):
    list_display = ['name', 'taskid', 'remark', 'create_date','arg']


# admin.site.register(TaskMeta, TaskMetaAdmin)
# admin.site.register(TaskSetMeta)
admin.site.register(TaskDetail,TaskDetailAdmin)
admin.site.register(TaskManualRecord)