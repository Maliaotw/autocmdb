
import uuid
from faker import Faker
import random

class IDRAC:

    def __init__(self):
        self.fake = Faker()
        self.data = {}
        self._basic()
        self._mem()
        self._cpu()
        self._disk()
        self._nic()

    def _basic(self):
        self.data.update({
            'basic': {
                'name': 'esxi-{}'.format(self.fake.bothify(text='?##', letters='AB')),
                'sn': uuid.uuid4().__str__(),
                'manufacturer': '',
                'model': random.choice(['PowerEdge R730','PowerEdge R740','PowerEdge R640']),
                'manage_ip': self.fake.ipv4_private(),
                'os_distribution': '',
                'os_platform': 'VMware ESXi 6.0.0',
                'os_version': 'Not Available',
                'total_cores': random.choice([64,32,128]),
                'total_disk': random.choice([512,10240,20480,30720]),
                'total_memory': random.choice([256,512,1024]),
                'enabled': True
            }}
        )

    def _mem(self):

        cards =  random.choice(list(range(1,4)))
        _data_list = []
        for i in range(1,cards+1):
            _data_list.append({
                'slot': f'DIMM.Socket.A{i}',
                'manufacturer': 'Micron Technology',
                'model': 'DDR4 DIMM',
                'capacity': '16',
                'sn': self.fake.bothify(text='1B###??#', letters='ABCDEFG'),
            })
        self.data.update({'mem':_data_list})

    def _cpu(self):
        cards =  random.choice(list(range(1,4)))
        _data_list = []
        for i in range(1,cards+1):
            _data_list.append({
                'slot': f'CPU.Socket.{i}',
                'manufacturer': 'Intel',
                'model': 'Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz',
                'cores': '8',
                'threads': '16',
            })
        self.data.update({'cpu':_data_list})

    def _disk(self):
        cards = random.choice(list(range(1, 4)))
        _data_list = []
        for i in range(1, cards+1):
            _data_list.append({
                'slot': f'Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-{i}',
                'manufacturer': 'TOSHIBA',
                'iface_type': 'SAS',
                'model': self.fake.bothify(text='??##??###??', letters='ABCDEFG'),
                'capacity': '558.38',
                'sn': self.fake.bothify(text='18?#?#???##?#', letters='ABCDEFG'),
            })
        self.data.update({'disk': _data_list})

    def _nic(self):
        cards = random.choice(list(range(1, 4)))
        _data_list = []
        for i in range(1, cards+1):
            _data_list.append({
                'name': f'NIC.Integrated.1-{i}-1',
                'ipaddress': self.fake.ipv4_private(),
                'model': 'Broadcom Gigabit Ethernet BCM5720',
                'macaddress': self.fake.mac_address(),
                'netmask': ''
            })
        self.data.update({'nic': _data_list})


    def to_dict(self):
        return self.data

if __name__ == '__main__':
    data = IDRAC().data
    print(data)


