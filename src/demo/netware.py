import uuid
from faker import Faker
import faker_microservice
import random
import string


class Netware:

    def __init__(self):
        self.fake = Faker()
        self.fake.add_provider(faker_microservice.Provider)

    @property
    def data(self):
        return random.choice(self._data())

    def _data(self):
        _data = [
            {
                'name': 'ASUS RT-AC88U',
                'model': 'RT-AC88U',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'ASUS',
                'sub_asset_type': 1
            },
            {
                'name': 'Cisco WS-C2960L-24TS-LL',
                'model': 'WS-C2960L-24TS-LL',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'Cisco',
                'sub_asset_type': 1
            },
            {
                'name': 'Cisco WS-C2960L-48TS-LL',
                'model': 'WS-C2960L-48TS-LL',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'Cisco',
                'sub_asset_type': 1
            },
            {
                'name': 'Dell N1524-24G',
                'model': 'N1524-24G',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'Dell',
                'sub_asset_type': 1
            },
            {
                'name': 'DrayTek Vigor2960',
                'model': 'Vigor2960',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'DrayTek',
                'sub_asset_type': 1
            },
            {
                'name': 'HPE 5130-48G',
                'model': 'JG934A',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'HP',
                'sub_asset_type': 1
            },
            {
                'name': 'HPE 5130-24G',
                'model': 'JG933A',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 24,
                'manufactory': 'HP',
                'sub_asset_type': 1
            },
            {
                'name': 'HPE 5130-48G-PoE',
                'model': 'JG941A',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 48,
                'manufactory': 'HP',
                'sub_asset_type': 1
            },
            {
                'name': 'FortiGate-100D',
                'model': 'FG-100D',
                'manage_ip': self.fake.ipv4_public(),
                'sn': str(uuid.uuid4()).split('-')[-1],
                'port_num': 16,
                'manufactory': 'FORTINET',
                'sub_asset_type': 3
            },
        ]
        return _data

    def to_dict(self):
        return self.data


if __name__ == '__main__':
    data = INSTANCE().data
    print(data)
