# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import ast
# from .tasks import ansible
import datetime
import logging

import pytz
from django.conf import settings
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from host import models as host_models
from src.base.permissions import WithBootstrapToken

logger = logging.getLogger(__name__)


class AssetsViewSet(GenericViewSet, mixins.RetrieveModelMixin ,generics.ListAPIView):
    permission_classes = [IsAuthenticated | WithBootstrapToken]


    def set_mem(self, h_obj, data):
        # models.Memory.objects.filter(slot="", manufacturer="", capacity="", host_obj="", model="", sn="")
        in_host = host_models.Memory.objects.filter(host_obj=h_obj)

        summary = []

        for i in data:
            if in_host.filter(slot=i['slot']):
                # 已存在 看差異
                if in_host.filter(manufacturer=i['manufacturer'], capacity=i['capacity'], slot=i['slot']):
                    logger.info("沒有變化")
                    # summary.append("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(slot=i['slot']).update(manufacturer=i['manufacturer'], capacity=i['capacity'])
                    summary.append("更新 %s %s" % (i['slot'], i['size']))

            else:
                logger.info("新增內存")
                host_models.Memory.objects.create(
                    manufacturer=i['manufacturer'],
                    capacity=i['capacity'],
                    slot=i['slot'],
                    host_obj=h_obj,
                    model=i['model'],
                    sn=i['sn']
                )
                summary.append("新增 %s %s" % (i['slot'], i['capacity']))

        if summary:
            summary.insert(0, "內存:")

        return summary

    def set_nic(self, h_obj, data):
        summary = []

        for i in data:
            # models.NIC.objects.filter(macaddress="", model="", netmask="", ipaddress="", name='')
            in_host = host_models.NIC.objects.filter(host_obj=h_obj)

            if in_host.filter(name=i['name']):
                # 已存在
                if in_host.filter(macaddress=i['macaddress'], ipaddress=i['ipaddress'], name=i['name']):
                    logger.info("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(name=i['name']).update(
                        macaddress=i['macaddress'],
                        ipaddress=i['ipaddress'],
                        netmask=i['netmask'],
                        model=i['model']
                    )
                    summary.append("更新 %s %s" % (i['name'], i['ipaddress']))
            else:
                logger.info("新增網卡")
                host_models.NIC.objects.create(
                    macaddress=i['macaddress'],
                    model=i['model'],
                    netmask=i['netmask'],
                    ipaddress=i['ipaddress'],
                    name=i['name'],
                    host_obj=h_obj
                )
                summary.append("新增 %s %s" % (i['name'], i['ipaddress']))

        if summary:
            summary.insert(0, "網卡:")

        return summary

    def set_disk(self, h_obj, data):
        summary = []

        for i in data:
            # models.Disk.objects.filter(slot="", model="", capacity="", host_obj="", sn="", manufacturer="", iface_type="")
            in_host = host_models.Disk.objects.filter(host_obj=h_obj)

            if in_host.filter(slot=i['slot']):
                # 已存在
                if in_host.filter(capacity=i['capacity'], slot=i['slot'], model=i['model']):
                    logger.info("沒有變化")
                    # summary.append("沒有變化")
                else:
                    logger.info("更新")
                    in_host.filter(slot=i['slot']).update(
                        capacity=i['capacity'],
                        slot=i['slot'],
                        model=i['model'],
                        sn=i['sn'],
                        manufacturer=i['manufacturer'],
                        iface_type=i['iface_type']
                    )
                    summary.append("更新 %s %s" % (i['slot'], i['capacity']))
            else:
                logger.info("新增硬盤")
                host_models.Disk.objects.create(
                    slot=i['slot'],
                    model=i['model'],
                    capacity=i['capacity'],
                    host_obj=h_obj,
                    sn=i['sn'],
                    manufacturer=i['manufacturer'],
                    iface_type=i['iface_type']
                )
                summary.append("新增 %s %s" % (i['slot'], i['capacity']))

        if summary:
            summary.insert(0, "硬盤:")

        return summary

    def set_cpu(self, h_obj, data):
        summary = []

        for i in data:
            # models.CPU.objects.filter(slot="",manufacturer="",model="",cores="",threads="",host_obj="")
            in_host = host_models.CPU.objects.filter(host_obj=h_obj)

            if in_host.filter(slot=i['slot']):
                # 已存在
                if in_host.filter(slot=i['slot'], model=i['cpu_model']):
                    logger.info("沒有變化")
                else:
                    in_host.filter(slot=i['slot']).update(
                        manufacturer=i['manufacturer'],
                        model=i['model'],
                        cores=i['cores'],
                        threads=i['threads']
                    )
                    summary.append("更新 %s %s" % (i['slot'], i['cores']))
            else:
                logger.info("新增CPU")
                host_models.CPU.objects.create(
                    slot=i['slot'],
                    manufacturer=i['manufacturer'],
                    model=i['model'],
                    cores=i['cores'],
                    host_obj=h_obj
                )
                summary.append("新增 %s %s" % (i['slot'], i['cores']))

        if summary:
            summary.insert(0, "CPU:")

        return summary

    def run(self, data):

        basic = data['basic']
        logger.info(f'basic {basic}')

        record = {'title': '', 'summary': []}

        node, created = host_models.Node.objects.get_or_create(name="-".join(basic['name'].split("-")[:-1]))

        remote_addr = self.request._request.META['REMOTE_ADDR']

        h_obj, created = host_models.Host.objects.get_or_create(
            name=basic['name'],
            sn=basic['sn'],
            node=node,
            cate=2,
            defaults={
                'manage_ip': basic['manage_ip'],
                'manage_ssh': basic['manage_ssh'],
                'model': basic['model'],
                'manufacturer': basic['manufacturer'],
                'os_platform': basic['os_platform'],
                'os_distribution': basic['os_distribution'],
                'os_version': basic['os_version'],
                'total_memory': sum([i['capacity'] for i in data['mem']]),
                'total_disk': sum([i['capacity'] for i in data['disk']]),
                'total_cores': sum([int(i['cores']) for i in data['cpu']]),
            }
        )
        if created:
            record['title'] = 'ADD %s' % h_obj.name

        # proc

        proclist = data.get('proc')
        hp = host_models.HostProc.objects.create(host=h_obj)
        for i in proclist:
            i['create_time'] = datetime.datetime.fromtimestamp(i['create_time']).replace(tzinfo=pytz.utc)
            proc_obj = host_models.Process.objects.create(**i)
            hp.proc.add(proc_obj)
        hp.save()

        # net
        netlist = data.get('net')
        hn = host_models.HostNet.objects.create(host=h_obj)
        for i in netlist:
            net_obj = host_models.Net.objects.create(**i)
            hn.net.add(net_obj)
        hn.save()

        record['summary'] += self.set_mem(h_obj, data['mem'])
        record['summary'] += self.set_nic(h_obj, data['nic'])
        record['summary'] += self.set_disk(h_obj, data['disk'])
        record['summary'] += self.set_cpu(h_obj, data['cpu'])

        if record['summary'] and not record['title']:
            record['title'] = '更新 %s' % h_obj.name
            ret = "Update %s" % h_obj.name

        if record['title']:
            # 建立資產變更紀錄表
            record['summary'] = "\n".join(record['summary'])
            host_models.HostRecord.objects.create(host_obj=h_obj, **record)
        else:
            record['title'] = 'Noting'

        return record['title']


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # logger.info(request.META)

        if settings.ENV_MODE == 'DEMO':
            from src.demo.instances import INSTANCE
            data = INSTANCE().data
            ret = self.run(data)
            return Response({'data': ret})


        data = ast.literal_eval(request.data)
        ret = self.run(data)

        return Response({'data': ret})


    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

