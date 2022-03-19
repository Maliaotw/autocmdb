from django.db import models

__all__ = ['VM']


# Create your models here.

class VM(models.Model):
    status_choice = ((1, 'running'), (2, 'stop'), (3, 'restart'), (4, '正在初始化中'), (5, '構建失敗'))

    name = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(choices=status_choice, default=4)
    check = models.CharField(max_length=64, default='')
    instance = models.OneToOneField('Instance', null=True, on_delete=models.DO_NOTHING)
    task = models.CharField(max_length=64, default='')
    is_finish = models.BooleanField(default=False)
    manage_ip = models.GenericIPAddressField(blank=True, null=True)
    latest_date = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.name, self.manage_ip)


class Instance(models.Model):
    """
    {
        "_ansible_no_log": False,
        "changed": True,
        "instance": {
            "annotation": "",
            "current_snapshot": None,
            "customvalues": {},
            "guest_consolidation_needed": False,
            "guest_question": None,
            "guest_tools_status": "guestToolsRunning",
            "guest_tools_version": "9536",
            "hw_cluster": None,
            "hw_cores_per_socket": 1,
            "hw_datastores": ["datastore1"],
            "hw_esxi_host": "172.16.10.16",
            "hw_eth0": {
                "addresstype": "assigned",
                "ipaddresses": ["172.16.10.170", "xxxxx::7808:a051:215d:9646"],
                "label": "Network adapter 1",
                "macaddress": "00:xx:xx:bf:f2:65",
                "macaddress_dash": "00-xx-xx-bf-f2-65",
                "portgroup_key": None,
                "portgroup_portkey": None,
                "summary": "VM Network",
            },
            "hw_files": [
                "[datastore1] demo-web1/demo-web1.vmx",
                "[datastore1] demo-web1/demo-web1.nvram",
                "[datastore1] demo-web1/demo-web1.vmsd",
                "[datastore1] demo-web1/demo-web1.vmdk",
            ],
            "hw_folder": "/BI/vm",
            "hw_guest_full_name": "CentOS 4/5/6/7 (64-bit)",
            "hw_guest_ha_state": None,
            "hw_guest_id": "centos64Guest",
            "hw_interfaces": ["eth0"],
            "hw_is_template": False,
            "hw_memtotal_mb": 512,
            "hw_name": "demo-web1",
            "hw_power_status": "poweredOn",
            "hw_processor_count": 1,
            "hw_product_uuid": "ddd993-87878-4614-ca8f-fe76f9ac876e",
            "hw_version": "vmx-11",
            "instance_uuid": "ddd993-87878-737a-8901-970f4f048b03",
            "ipv4": "172.16.10.14",
            "ipv6": None,
            "module_hw": True,
            "snapshots": [],
            "vnc": {},
        },
        "invocation": {
            "module_args": {
                "annotation": None,
                "cdrom": {},
                "cluster": None,
                "convert": None,
                "customization": {},
                "customization_spec": None,
                "customvalues": [],
                "datacenter": "BI",
                "datastore": None,
                "disk": [
                    {"datastore": "datastore1", "size_gb": "20", "type": "eagerzeroedthick"}
                ],
                "esxi_hostname": None,
                "folder": "",
                "force": False,
                "guest_id": None,
                "hardware": {
                    "hotadd_cpu": True,
                    "hotadd_memory": True,
                    "hotremove_cpu": True,
                    "memory_mb": "512",
                    "num_cpus": "1",
                    "scsi": "paravirtual",
                },
                "hostname": "172.16.10.60",
                "is_template": False,
                "linked_clone": False,
                "name": "demo-web1",
                "name_match": "first",
                "networks": [],
                "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
                "port": 443,
                "resource_pool": None,
                "snapshot_src": None,
                "state": "present",
                "state_change_timeout": 0,
                "template": "centos7",
                "use_instance_uuid": False,
                "username": "administrator@example.com",
                "uuid": None,
                "validate_certs": False,
                "vapp_properties": [],
                "wait_for_customization": False,
                "wait_for_ip_address": True,
            }
        },
    }

    """
    pass

