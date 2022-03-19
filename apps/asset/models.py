from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

__all__ = ["Tag", "Asset", "IDC", "Rack", "RackUnit", 'NetworkDevice', 'ISP']


# Create your models here.

class Tag(models.Model):
    """
    資產標籤
    """
    name = models.CharField('標籤', max_length=64)
    remark = models.TextField(verbose_name="備註", blank=True)

    class Meta:
        verbose_name_plural = "標籤表"

    def __str__(self):
        return self.name


class IDC(models.Model):
    """
    機房資訊
    """
    name = models.CharField('機房', max_length=32)
    floor = models.IntegerField('樓層')

    class Meta:
        verbose_name_plural = "機房表"

    def __str__(self):
        return "%s機房 %sF" % (self.name, self.floor)


class Rack(models.Model):
    """機櫃"""

    idc = models.ForeignKey(verbose_name="機房", to="IDC", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="機櫃號", max_length=32)
    height = models.SmallIntegerField(verbose_name="高度", default=42)
    max_power = models.PositiveSmallIntegerField(verbose_name="最大功率", default=0)
    remark = models.TextField(verbose_name="備註", blank=True)
    isp = models.ManyToManyField('ISP', verbose_name='ISP')

    def __str__(self):
        return "%s" % (self.name)


class RackUnit(models.Model):
    """機櫃使用表"""

    position_choice = ((1, 'Front'), (2, 'Back'))

    name = models.ForeignKey("Rack", on_delete=models.CASCADE)
    asset = models.ForeignKey("Asset", on_delete=models.CASCADE)
    num = models.SmallIntegerField(blank=True, null=True)
    position = models.PositiveSmallIntegerField(choices=position_choice, default=1, blank=True, null=True)

    def __str__(self):
        return "%s %s" % (self.name, self.asset)


class Asset(models.Model):
    """資產資訊表，所有資產公共資訊（交換機，伺服器，防火牆等）
    """

    device_type_choices = (
        (1, '服務器'),
        (2, '網路設備'),
    )
    device_status_choices = (
        (1, '上架'),
        (2, '線上'),
        (3, '離線'),
        (4, '下架'),
    )

    rack = models.ForeignKey("Rack", verbose_name='機櫃', blank=True, null=True, on_delete=models.CASCADE)
    # node
    # host = models.OneToOneField("Host", related_name="+")
    device_type_id = models.SmallIntegerField(choices=device_type_choices, default=1)
    device_status_id = models.SmallIntegerField(verbose_name='狀態', choices=device_status_choices, default=1)

    tag = models.ForeignKey('Tag', verbose_name='標籤', null=True, blank=True, on_delete=models.CASCADE)

    latest_date = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    # --- 關聯網路設備 服務器
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()

    # 不會生成字段 用於['host'.'交換器','防火牆']
    content_object = GenericForeignKey("content_type", "object_id")

    size = models.SmallIntegerField(verbose_name='機型大小(U)', default=1)

    # 用於同步關聯網路設備、服務器 名稱 方便查詢
    name = models.CharField(verbose_name='名稱', max_length=64)

    number = models.CharField(verbose_name='資產編號', max_length=255, blank=True, null=True)

    def get_cpu_info(self):
        if self.device_type_id == 1:
            return self.content_object.cpu.all()
        else:
            return None

    def get_nic_info(self):
        if self.device_type_id == 1:
            return self.content_object.nic.all()
        else:
            return None

    def get_disk_info(self):
        if self.device_type_id == 1:
            return self.content_object.disk.all()
        else:
            return None

    def get_mem_info(self):
        if self.device_type_id == 1:
            return self.content_object.memory.all()
        else:
            return None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        d = {'host': 1, 'asset': 2}
        self.device_type_id = d[self.content_type.app_label]

        self.name = self.content_object.name
        # 如果有rack, 則創建rackunit
        if self.rack:
            # print('self.rack', self.rack)
            if RackUnit.objects.filter(asset=self):
                rackunit_obj = RackUnit.objects.filter(asset=self).first()
                rackunit_obj.name = self.rack
                rackunit_obj.save()
            else:
                RackUnit.objects.get_or_create(name=self.rack, asset=self)

        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def __str__(self):
        return self.get_device_type_id_display()

    class Meta:
        verbose_name_plural = "資產表"
        verbose_name = '資產'


class ISP(models.Model):
    name = models.CharField(verbose_name='名稱', max_length=255)
    ip_range = models.CharField(verbose_name='IP範圍', max_length=64)
    netmask = models.CharField(verbose_name='NETMASK', max_length=64)
    geteway = models.CharField(verbose_name='GETEWAY', max_length=64)
    remark = models.TextField(verbose_name='備註', null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.name, self.ip_range)

    class Meta:
        verbose_name = 'ISP'
        verbose_name_plural = 'ISP'


# Create your models here.
class NetworkDevice(models.Model):
    '''網絡設備'''

    type_choices = (
        (1, '路由器'),
        (2, '交換機'),
        (3, '防火牆'),
    )

    sub_asset_type = models.SmallIntegerField(choices=type_choices, verbose_name="設備類型", default=2)
    name = models.CharField(verbose_name='設備名稱', max_length=64)
    manage_ip = models.CharField('管理IP', max_length=64, blank=True, null=True)
    intranet_ip = models.GenericIPAddressField('內網IP', blank=True, null=True)
    sn = models.CharField('SN號', max_length=128, unique=True)
    manufactory = models.CharField(verbose_name='製造商', max_length=128, null=True, blank=True)
    model = models.CharField('型號', max_length=128, null=True, blank=True)
    port_num = models.SmallIntegerField('端口個數', null=True, blank=True)
    detail = models.TextField('備註', null=True, blank=True)
    latest_date = models.DateTimeField(verbose_name='更新日期', auto_now=True)
    create_date = models.DateTimeField(verbose_name='創建日期', auto_now_add=True)
    warranty_date = models.DateField(verbose_name='保固日期', blank=True, null=True)

    # 只關聯不會生成字段
    asset = GenericRelation(to='Asset')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

        # print(self.asset.all())
        if not self.asset.all():
            Asset.objects.create(content_object=self)

    def __str__(self):
        return "%s" % self.model

    class Meta:
        verbose_name = '網絡設備'
