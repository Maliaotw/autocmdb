#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : tasks
# @Date     : 2019-08-12
# @Author   : maliao
# @Link     : None

import datetime
from celery import shared_task, Task, subtask
import time
from django.core.cache import cache
from src import ansiblerunner
from host import models as host_models
from src.redisbase import RedisQueue
from django.contrib.auth.models import User
import tempfile


def get_hostdata(hostids):
    host_data = []
    host_objs = []
    for id in hostids:
        host_obj = host_models.Host.objects.get(id=id)
        host_objs.append(host_obj)
        # TODO 改成 執行用戶
        data = {
            "hostname": host_obj.name,
            "ip": host_obj.manage_ip,
            "port": host_obj.manage_ssh,
            "username": "root",
            "private_key": "/Users/maliao/.ssh/id_rsa"
        }
        host_data.append(data)

    return {'data':host_data,'objs':host_objs}

@shared_task()
def pb(hostids,command,uuid4,userid):
    hostdata = get_hostdata(hostids)

    yaml_path = tempfile.mktemp(suffix='.yml')
    f = open(yaml_path,'w')
    f.write(command)
    f.close()

    # print(hostdata['data'])
    date_start = datetime.datetime.now()

    c = ansiblerunner.PlayBookRunner(
        hostname=uuid4,
        path=yaml_path,
        inventory=hostdata['data']
    )
    # print(c)
    ret = c.run()
    # print(ret)

    date_finished = datetime.datetime.now()
    user = User.objects.get(id=userid)
    # # 保存命令歷史
    cr_obj = host_models.CmdRecord(
        user=user,
        command=command,
        _result="\r\n".join(ret),
        is_finished=True,
        date_start=date_start,
        date_finished=date_finished

    )
    cr_obj.save()

    for h in hostdata['objs']:
        cr_obj.host.add(h)

    rq = RedisQueue(uuid4)

    # print('加入隊列')
    rq.put('end')
    # print('end')

    return {'data':'ok'}