import datetime
from celery import shared_task, Task, subtask
import time
from django.core.cache import cache
from src.ansiblerunner import PlayBookRunner, AdHocRunner, BaseInventory
from celery.result import AsyncResult
from django.conf import settings
import os
from config.celery import app
from . import models

@shared_task
def hello(name='Maliao', callback=None, date=datetime.datetime.now(), **kwargs):
    # print('callback', callback)
    # print('kwargs', kwargs)
    hello.app.startdate = datetime.datetime.now()
    hello.app.name = 'hello'
    # print(hello._app)
    for i in range(10):
        time.sleep(1)
        # print(i)
        cache.set(name, i, 5)

    return {"data": "Hello {}".format(name)}


@shared_task
def init_vm(name, memory_mb, size_gb, num_cpus, callback=None, date=datetime.datetime.now(), **kwargs):
    """

    :param name:
    :param memory_mb:
    :param size_gb:
    :param num_cpus:
    :param callback:
    :param date:
    :param kwargs:
    :return:
    """

    # t2 =tasks.init_vm.delay(name='demo2',memory_mb=1024,size_gb=20,num_cpus=1)

    hostname = name
    option = {'newhost': hostname, 'memory_mb': memory_mb, 'size_gb': size_gb, 'num_cpus': num_cpus}
    option.update(settings.VCENTER)  # 加入Vcenter變數
    pems_dir = os.path.join(settings.APPS_DIR, 'vm/pems')
    yaml_dir = os.path.join(settings.APPS_DIR, 'vm/yaml')
    pem_path = "%s/%s.pem" % (pems_dir, hostname)

    data = cache.get(name)
    data.update({'status': '開始初始化中', 'check': ''})
    cache.set(name, data)

    # --- 開始初始化中
    c = PlayBookRunner(
        hostname=hostname,
        path="%s/%s" % (yaml_dir, 'vm_create.yml'),
        options=option,
    )
    # print(c)
    c.run()
    r = c.get_result

    ip = r['instance']['ipv4']
    data = cache.get(name)
    data.update({'status': '初始化中', 'check': '1/2 check pass', 'manage_ip': ip})
    cache.set(name, data)

    # --- init

    init = PlayBookRunner(
        hostname=hostname,
        path="%s/%s" % (yaml_dir, "vm_init.yml"),
        options={
            'hostname': hostname,
            'pem_path': pem_path
        },
        inventory={
            "ip": ip,
            "port": 22,
            "username": "root",
            "password": "065ef44c12cf636f0574db9b",
        }
    )

    init.run()


    # --- 完成
    data = cache.get(name)
    data.update({'status': 'running', 'check': '2/2 check pass', 'is_finish':'True'})
    cache.set(name, data)  # 只保留10秒

    # 錄入數據

    return {"data": "構建成功 {}".format(name)}


@app.task
def add(x, y):
    return x + y


@shared_task
def t1():
    host_data = [
        {
            "hostname": "testserver1",
            "ip": "192.168.33.101",
            "port": 22,
            "username": "maliao",
            "password": "123456",
        },
    ]
    inventory = BaseInventory(host_data)
    runner = AdHocRunner(inventory)

    tasks = [
        {"action": {"module": "shell", "args": "ls"}, "name": "run_cmd"},
        {"action": {"module": "shell", "args": "whoami"}, "name": "run_whoami"},
    ]
    ret = runner.run(tasks, "all")
    return {'ret': 'ok'}


@shared_task
def t2():
    c = PlayBookRunner(
        hostname='hostname',
        path="/Users/maliao/PycharmProjects/AutoCmdb/vSphere/yml/create_vm.yml",
        options={'newhost': 'hostname', 'memory_mb': 512, 'size_gb': 20, 'num_cpus': 1})
    print(c)
    print(c.run())

    return {'ret': 'ok'}


@app.task
def t3():
    hostname = 'maliao-web101'

    c = PlayBookRunner(
        hostname=hostname,
        path="/Users/maliao/PycharmProjects/AutoCmdb/vSphere/yml/create_vm.yml",
        options={'newhost': hostname, 'memory_mb': 512, 'size_gb': 20, 'num_cpus': 1})

    r = c.run()
    print(r)
    ip = r['instance']['ipv4']

    init = PlayBookRunner(
        hostname=hostname,
        path='/Users/maliao/PycharmProjects/AutoCmdb/vSphere/yml/vm_init.yml',
        options={'hostname': hostname},
        inventory={
            "ip": ip,
            "port": 22,
            "username": "root",
            "password": "065ef44c12cf636f0574db9b",
        }

    )

    init.run()

    return {'ret': 'ok'}


@app.task
def vm_destroy():
    # 銷毀
    vm_obj = models.VM.objects.filter(is_finish=True,status=5)
    for vm in vm_obj:
        hostname = vm.name
        option = {'newhost': hostname}
        option.update(settings.VCENTER)  # 加入Vcenter變數
        yaml_path = os.path.join(settings.BASE_DIR, 'vm/yaml')

        c = PlayBookRunner(
            hostname=hostname,
            path="%s/%s" % (yaml_path, 'vm_destroy.yml'),
            options=option,
        )
        # print(c)
        c.run()
        r = c.get_result
        vm.delete()
        print('銷毀完成')
        # data = cache.get(hostname)
        # data.update({'status': '銷毀完成', 'check': ''})
        # cache.set(hostname, data)


