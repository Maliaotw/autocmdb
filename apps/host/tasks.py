from celery import shared_task, Task, subtask
import json

# model
from django_celery_beat import models as djcelery_model
from django_celery_results import models as djresults_model
from tasks import models as task_model
from host import models as host_models
from asset import models as asset_models
import datetime
from src.dell import DellEMC
from django.conf import settings

class TaskHistoryMixin:

    def to_database(self, name, task_id, arg, kwargs):
        # print('self._app: %s' % self._app)
        # print('self._app.startdate: %s' % self._app.startdate)
        argval = arg or kwargs
        name = djcelery_model.PeriodicTask.objects.get(name=self._app.name)
        # taskid = djcelery_model.TaskMeta.objects.get(task_id=task_id)
        taskid = djresults_model.TaskResult.objects.get(task_id=task_id)
        taskdetail = task_model.TaskDetail.objects.create(
            create_date=self._app.startdate, name=name, taskid=taskid, arg=argval
        )

        # print('追加紀錄')
        return taskdetail


class BaseTask(Task, TaskHistoryMixin):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # print("任務錯誤 Error")
        # print("%s %s %s %s" % (self.name,task_id, args, kwargs))
        self.to_database(self.name, task_id, args, kwargs)

        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        # print("任務成功 Success")
        self.to_database(self.name, task_id, args, kwargs)

        return super().on_success(retval, task_id, args, kwargs)


@shared_task(base=BaseTask)
def hello(name='Maliao', callback=None, date=datetime.datetime.now(), **kwargs):
    # print('callback', callback)
    # print('kwargs', kwargs)
    hello.app.startdate = datetime.datetime.now()
    hello.app.name = 'hello'
    # print(hello._app)

    return {"data": "Hello {}".format(name)}


def set_cpu(h_obj, data):
    summary = []
    # CPU
    for i in data:
        if h_obj.cpu.filter(slot=i['slot']):
            # 存在
            cpu_obj = h_obj.cpu.filter(slot=i['slot'])
            if cpu_obj.filter(cores=i['cores']):
                # 沒有變化
                pass
            else:
                # 更新
                cpu_obj = cpu_obj.first()
                i.pop('slot')
                i.pop('cores')
                for k, v in i.items():
                    setattr(cpu_obj, k, v)
                cpu_obj.save()

                summary.append("更新 %s %s" % (i['slot'], i['cores']))


        else:
            # 新增
            host_models.CPU.objects.create(host_obj=h_obj, **i)
            summary.append("新增 %s %s" % (i['slot'], i['cores']))

    if summary:
        summary.insert(0, "CPU:")

    return summary

def set_disk(h_obj, data):
    # 硬盤
    summary = []

    for i in data:
        if h_obj.disk.filter(slot=i['slot']):
            disk_obj = h_obj.disk.filter(slot=i['slot'])
            if disk_obj.filter(capacity=i['capacity'], sn=i['sn']):
                # 沒有變化
                pass
            else:
                disk_obj = disk_obj.first()
                for k, v in i.items():
                    setattr(disk_obj, k, v)
                disk_obj.save()
                summary.append("更新 %s %s" % (i['slot'], i['capacity']))


        else:
            host_models.Disk.objects.create(host_obj=h_obj, **i)
            summary.append("新增 %s %s" % (i['slot'], i['capacity']))

    if summary:
        summary.insert(0, "硬盤:")

    return summary

@shared_task(base=BaseTask)
def idracinfo(iid,debug=True):
    idrac_obj = host_models.idrac.objects.get(id=iid)
    idracinfo.app.startdate = datetime.datetime.now()
    idracinfo.app.name = idrac_obj.idrac_ip

    if settings.ENV_MODE == 'DEMO':
        from src.demo.idrac import IDRAC
        data = IDRAC().data
        data['basic'].update({'manage_ip':idrac_obj.idrac_ip})


    else:

        dell_obj = DellEMC(idrac_obj.idrac_ip, idrac_obj.user, idrac_obj.passwd)
        data = dell_obj.run()
        dell_obj.racadm.client.close()

    record = {'title': '', 'summary': []}


    if not idrac_obj.host:
        # print('新增')
        msg = "新增"


        basic = data['basic']
        host_obj = host_models.Host.objects.create(**basic)

        idrac_obj.host = host_obj
        idrac_obj.save()

        for i in data['mem']:
            host_models.Memory.objects.create(slot=i['slot'], host_obj=host_obj)

        for i in data['nic']:
            host_models.NIC.objects.create(host_obj=host_obj,**i)

        for i in data['disk']:
            host_models.Disk.objects.create(host_obj=host_obj,**i)

        for i in data['cpu']:
            host_models.CPU.objects.create(host_obj=host_obj,**i)

        asset_models.Asset.objects.create(content_object=host_obj)

        record['title'] = '新增 %s' % host_obj.name

    else:
        # print("更新")
        msg = "更新"

        # 硬件
        host_obj = idrac_obj.host
        for k,v in data['basic'].items():
            setattr(host_obj,k,v)
        host_obj.save()


    record['summary'] += set_cpu(host_obj, data['cpu'])
    record['summary'] += set_disk(host_obj, data['disk'])

    if record['summary'] and not record['title']:
        record['title'] = '更新 %s' % host_obj.name

    if record['title']:
        # 建立資產變更紀錄表
        record['summary'] = "\n".join(record['summary'])
        host_models.HostRecord.objects.create(host_obj=host_obj, **record)




    return {"data": msg}
