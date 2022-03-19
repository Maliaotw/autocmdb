
import uuid
from faker import Faker
import faker_microservice
import random
import string

class INSTANCE:

    def __init__(self):
        self.fake = Faker()
        self.fake.add_provider(faker_microservice.Provider)
        self.data = {}
        self._basic()
        self._mem()
        self._cpu()
        self._disk()
        self._nic()
        self._proc()
        self._net()

    def _basic(self):
        self.data.update({
            'basic': {
                'name': self.fake.bothify(text='?##-web#', letters=string.ascii_lowercase),
                'sn': uuid.uuid4().__str__(),
                'manufacturer': 'Alibaba Cloud',
                'model': random.choice(['Alibaba Cloud ECS']),
                'manage_ip': self.fake.ipv4_public(),
                'os_distribution': 'Linux',
                'os_platform': 'Linux',
                'os_version': 'CentOS Linux release 7.6.1810 (Core) ',
                'total_cores': random.choice([2,4,8]),
                'total_disk': random.choice([20,40,100]),
                'total_memory': random.choice([4,8,16]),
                'enabled': False,
                'cate':2,
                'manage_ssh':22
            }}
        )

    def _mem(self):

        cards = random.choice(list(range(1,4)))
        _data_list = []
        for i in range(1,cards+1):
            _data_list.append({
                'slot': f'DIMM {i}',
                'manufacturer': 'Alibaba Cloud',
                'model': 'DIMM RAM',
                'capacity': 4,
                'sn': self.fake.bothify(text='1B###??#', letters='ABCDEFG'),
            })
        self.data.update({'mem':_data_list})

    def _cpu(self):
        cards =  random.choice(list(range(1,4)))
        _data_list = []
        for i in range(1,cards+1):
            _data_list.append({
                'slot': f'CPU {i}',
                'manufacturer': 'Intel Corp.',
                'model': 'Intel(R) Xeon(R) Platinum 8163 CPU @ 2.50GHz',
                'cores': '2',
                'threads': '1',
            })
        self.data.update({'cpu':_data_list})

    def _disk(self):
        cards = random.choice(list(range(1, 4)))
        _data_list = []
        disk_slot = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
        for i in range(1, cards+1):
            _data_list.append({
                'slot': f'/dev/vd{disk_slot[i]}',
                'manufacturer': '',
                'iface_type': 'virtio',
                'model': 'Virtual I/O device',
                'capacity': 100,
                'sn': '',
            })
        self.data.update({'disk': _data_list})

    def _nic(self):
        cards = 1
        _data_list = []
        for i in range(1, cards+1):
            _data_list.append({
                'name': f'eth{i}',
                'ipaddress': self.fake.ipv4_private(),
                'model': 'Ethernet interface',
                'macaddress': self.fake.mac_address(),
                'netmask': '255.255.255.0'
            })
        self.data.update({'nic': _data_list})

    def _proc(self):
        _data_list = []
        for i in range(random.randint(1,100)):
            name = self.fake.microservice()
            _data_list.append({
                'name': f'{name}',
                 'status': random.choice(['sleeping','run']),
                 'username': 'root',
                 'create_time': 1568100982.13,
                 'pid': random.randint(1,12000),
                 'cmdline': [f'/usr/lib/systemd/{name}']
            })

        self.data.update({'proc': _data_list})

    def _net(self):
        _data_list = []
        for i in range(random.randint(1,100)):
            _data_list.append({
                'proto': 'tcp',
                 'port': random.randint(1,65535),
                 'pid': random.randint(1,12000),
                'name': self.fake.microservice()
            })

        self.data.update({'net': _data_list})

    def to_dict(self):
        return self.data

if __name__ == '__main__':
    data = INSTANCE().data
    print(data)


