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
from src.ansiblerunner import BaseInventory,CommandRunner


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


@shared_task(soft_time_limit=60)
def ansible(host_data=[], command='ls', uuid=''):


    inventory = BaseInventory(host_data)
    runner = CommandRunner(inventory)
    tasks = [
        {"action": {"module": "ping", "data": "pong"}, "name": "check connect to host"},
    ]

    # TODO try

    result = runner.run(tasks=tasks, pattern='all', play_name=uuid)

    # print('res.results_command', result.results_command)
    # print('res.results_raw', result.results_raw)
    # print(res.re)
    return {"data": result.results_command}

