from django.db.models.signals import post_save
from django.core.cache import cache
from . import tasks
from .models import VM
from django.dispatch import receiver
from django.conf import settings
import uuid
import random
from faker import Faker
import os
from shutil import copyfile
import paramiko

"""
pre_init                    # django的modal执行其构造方法前，自动触发
post_init                   # django的modal执行其构造方法后，自动触发
pre_save                    # django的modal对象保存前，自动触发
post_save                   # django的modal对象保存后，自动触发
pre_delete                  # django的modal对象删除前，自动触发
post_delete                 # django的modal对象删除后，自动触发
m2m_changed                 # django的modal中使用m2m字段操作第三张表（add,remove,clear）前后，自动触发
class_prepared              # 程序启动时，检测已注册的app中modal类，对于每一个类，自动触发
"""


@receiver(post_save, sender=VM)
def on_vm_save(sender, instance: VM = None, created=True, **kwargs):
    """虛擬機初始化
    1. 發送異步任務
    2. ansible初始化(待優化)
    3. websocket查看狀態
    VM object
        {
            'signal': <django.db.models.signals.ModelSignal object at 0x10c49fda0>,
            'created': True,
            'update_fields': None,
            'raw': False,
            'using': 'default'
        }
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if created:
        if settings.ENV_MODE == 'DEMO':
            fake = Faker()
            instance.task = str(uuid.uuid4())
            instance.status = random.randint(1, 4)
            instance.status = random.randint(1, 4)

            if instance.status == 1:
                # 1/2 check pass
                instance.check = f'{random.randint(1, 2)}/2 check pass'
                instance.is_finish = True

            instance.manage_ip = fake.ipv4_public()

            pem = paramiko.RSAKey.generate(512)
            pem.write_private_key_file(os.path.join(settings.PEMS_ROOT, f'{instance.name}.pem'))
            # copyfile(os.path.join(settings.PEMS_ROOT,'demo.pem'), os.path.join(settings.PEMS_ROOT,f'{instance.name}.pem'))



        else:
            data = cache.get(instance.name)
            task = tasks.init_vm.delay(**data)
            data.update({'task': task.id})
            # print(task.id)
            cache.set(instance.name, data)
            instance.task = task.id

        instance.save()
