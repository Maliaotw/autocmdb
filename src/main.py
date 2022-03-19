# -*- coding: utf-8 -*-
#


from runner import PlayBookRunner,BaseInventory,CommandRunner
import os
import uuid


def play():
    BASE_DIR = os.getcwd()
    print(BASE_DIR)

    YML = os.path.join(BASE_DIR, 'yml')

    hostname = 'maliao-web101'
    c = PlayBookRunner(
        hostname=hostname,
        path="%s/test.yml" % YML,
        # options={'newhost': hostname, 'memory_mb': 512, 'size_gb': 20, 'num_cpus': 1}
    )
    c.run()

def runner():
    host_data = []
    data = {
        "hostname": 'jumpserver',
        "ip": '172.16.10.215',
        "port": 2222,
        "username": "root",
        "private_key": "/Users/maliao/.ssh/id_rsa"
    }
    host_data.append(data)


    inventory = BaseInventory(host_data)
    runner = CommandRunner(inventory)
    # tasks = [
    #     {"action": {"module": "ping", "data": "pong"}, "name": "check connect to host"},
    # ]

    # TODO try

    # date_start = datetime.datetime.now()
    # result = runner.run(tasks=tasks, pattern='all',uuid=uuid)
    result = runner.execute(cmd='ls', pattern='all', uuid=uuid.uuid4())
    print(result)

if __name__ == '__main__':
    runner()




