import requests
import paramiko
import re


class Racadm:

    def __init__(self, ip, user, passwd):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(ip, username=user, password=passwd, timeout=20)

    def exec_command(self, line):
        stdin, stdout, stderr = self.client.exec_command(line)
        return stdout.read().decode('utf8')


class DellEMC:

    def __init__(self, ip, user, passwd):
        self.racadm = Racadm(ip, user, passwd)
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.ret = {
            'mem': [],
            'nic': [],
            'disk': [],
            'cpu': [],
            'basic': {

            }
        }

    def _request(self, api):
        r = requests.get('https://%s%s' % (self.ip, api), verify=False, auth=(self.user, self.passwd))
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            return False

    def get_ipv4(self):
        data = self.racadm.exec_command('racadm get iDRAC.IPv4')

        # print(data)
        address = re.findall(r'Address=(.*)', data)[0]
        gateway = re.findall(r'Gateway=(.*)', data)[0]
        netmask = re.findall(r'Netmask=(.*)', data)[0]
        print(address, gateway, netmask)

    def getsysinfo(self):
        data = self.racadm.exec_command("racadm getsysinfo")
        ret = {
            'os_platform': re.findall('OS Name.\s*=\s*(.+\S)\s*', data)[0],
            'os_version': re.findall('\sOS Version\s*=\s(.*)\s*', data)[0],
            'manage_ip': re.findall('Current IP Address\s*=\s*(\S*)\s*', data)[0],
        }
        return ret

    def get_redfish_basic(self):

        data = self._request('/redfish/v1/Systems/System.Embedded.1')

        ret = {
            'sn': data.get('UUID'),
            # 'sn': data.get('SerialNumber'),
            'name': data.get('HostName'),
            'model': data.get('Model'),
            'manufacturer': data.get('Manufacturer'),
            'total_memory': data['MemorySummary']['TotalSystemMemoryGiB']
        }
        return ret

    def basic(self):

        data = {}
        d1 = self.getsysinfo()
        d2 = self.get_redfish_basic()

        data.update(d1)
        data.update(d2)
        return data

    def get_disk(self):
        data = self.racadm.exec_command('racadm storage get pdisks -o')
        # print(data)

        diskdata = []
        d = []
        num = 0
        for i in data.split("\n"):

            if "Disk.Bay." in i:

                if num == 0:
                    pass
                else:
                    diskdata.append("\n".join(d))
                    d.clear()
                num += 1

            else:
                d.append("%s\n" % i)

        diskdata.append("\n".join(d))
        # print(diskdata)
        # print(num)

        return diskdata

    def disk(self):
        ret = []

        for i in self.get_disk():
            ret.append({
                'capacity': re.findall('Size.*=\s(.\S*)\s*', i)[0],
                'manufacturer': re.findall('Manufacturer.*=\s(.\S*)\s*', i)[0],
                'slot': re.findall('Name.*=\s(.+\S)\s*', i)[0],
                'sn': re.findall('SerialNumber.*=\s(.+\S)\s*', i)[0],
                'iface_type': re.findall('BusProtocol.*=\s(.+\S)\s*', i)[0]
            })

        # print(ret)
        return ret

    def memory(self):
        data = self.racadm.exec_command('racadm getsensorinfo')
        ret = []
        for i in data.split('\n'):
            if 'System Board DIMM PG' in i:
                pass
            elif "DIMM" in i:
                # print(i)
                status = re.findall(r'DIMM [A-Z]\d\s*(\w+)\s*', i)[0]
                name = re.findall('DIMM [A-Z]\d', i)[0]
                if status == 'Ok':
                    ret.append({'status': status, 'slot': name})

        return ret

    def nic(self):
        data = self.racadm.exec_command('racadm getsysinfo')

        ret = []
        for i in data.split('\n'):
            if 'NIC.' in i:
                fildata = list(filter(lambda x: x, i.split(' ')))
                name = fildata[0]
                macaddress = fildata[-1]
                ret.append({
                    'name': name,
                    'macaddress': macaddress
                })

        # print(ret)
        return ret

    def cpu(self):
        ret = []

        cpulist = self._request('/redfish/v1/Systems/System.Embedded.1/Processors')
        for i in cpulist['Members']:
            data = self._request(i['@odata.id'])
            d = {
                'model': data['Model'],
                'manufacturer': data['Manufacturer'],
                'slot': data['Socket'],
                'cores': data['TotalCores'],

            }
            ret.append(d)

        # print(ret)
        return ret

    def run(self):

        ret = self.ret
        ret['basic'] = self.basic()
        ret['mem'] = self.memory()
        ret['nic'] = self.nic()
        ret['cpu'] = self.cpu()
        ret['disk'] = self.disk()

        d3 = {
            'total_cores': sum([int(i['cores']) for i in ret['cpu']]),
            'total_disk': sum([int(float(i['capacity'])) for i in ret['disk']]),
        }
        ret['basic'].update(d3)

        # print(ret)
        return ret


if __name__ == '__main__':
    ip = '172.16.10.1'
    user = 'cmdb'
    passwd = '893d7c848e7912fd7f7a16b4'
    d = DellEMC(ip, user, passwd)
    # print(d.cpu())
    d.racadm.client.close()
