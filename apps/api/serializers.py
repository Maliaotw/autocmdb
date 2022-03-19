from rest_framework import serializers
from django_celery_results import models as dcr_models
from host import models as host_models


class TaskResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dcr_models.TaskResult
        fields = ('id', 'status', 'result', 'traceback')

class CmdRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = host_models.CmdRecord
        fields = ('id', '_result')



class HostSerializer(serializers.ModelSerializer):
    pId = serializers.SerializerMethodField()

    @staticmethod
    def get_pId(obj):
        return obj.node.id

    class Meta:
        model = host_models.Host
        fields = ['id', 'name','node','pId']



class NodeSerializer(serializers.ModelSerializer):
    host_set = serializers.StringRelatedField(many=True)
    text = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    nodes = serializers.SerializerMethodField()

    @staticmethod
    def get_text(obj):
        return obj.name

    @staticmethod
    def get_tags(obj):
        return [str(obj.host_set.all().count())]

    @staticmethod
    def get_nodes(obj):
        # print(self.host_set)
        return [{'text':i.name,'id':i.id} for i in obj.host_set.all()]

    class Meta:
        model = host_models.Host
        fields = ['id','name', 'host_set','text','tags','nodes']
        read_only_fields = [
            'id', 'text', 'tags', 'nodes',
        ]