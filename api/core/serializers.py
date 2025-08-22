# monitoring/serializers.py
from rest_framework import serializers
from .models import Host, Process


# ---------- READ SERIALIZERS ----------

class ProcessTreeReadSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = ["pid", "name", "cpu_usage", "memory_usage", "children"]

    def get_children(self, obj):
        # recursive children
        qs = obj.children.all().order_by("pid")
        return ProcessTreeReadSerializer(qs, many=True).data


class HostReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = [
            "id",
            "hostname",
            "operating_system",
            "processor",
            "num_cores",
            "num_threads",
            "ram_total",
            "ram_used",
            "ram_available",
            "storage_total",
            "storage_used",
            "storage_free",
            "last_updated",
        ]


# ---------- INGEST SERIALIZERS (WRITE) ----------

class ProcessTreeIngestSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    cpu = serializers.FloatField(required=False, allow_null=True)       # from agent
    memory = serializers.FloatField(required=False, allow_null=True)    # MB
    children = serializers.ListField(child=serializers.DictField(), required=False)

    def to_internal_value(self, data):
        # Normalize keys to our model fields
        data = super().to_internal_value(data)
        data["cpu_usage"] = data.pop("cpu", None)
        data["memory_usage"] = data.pop("memory", None)
        return data


class HostIngestSerializer(serializers.Serializer):
    hostname = serializers.CharField(max_length=255)

    # system info
    operating_system = serializers.CharField(required=False, allow_blank=True, default="")
    processor = serializers.CharField(required=False, allow_blank=True, default="")
    num_cores = serializers.IntegerField(required=False, default=0)
    num_threads = serializers.IntegerField(required=False, default=0)

    ram_total = serializers.IntegerField(required=False, default=0)
    ram_used = serializers.IntegerField(required=False, default=0)
    ram_available = serializers.IntegerField(required=False, default=0)

    storage_total = serializers.IntegerField(required=False, default=0)
    storage_used = serializers.IntegerField(required=False, default=0)
    storage_free = serializers.IntegerField(required=False, default=0)

    # processes as a tree
    processes = serializers.ListField(child=ProcessTreeIngestSerializer(), required=True)
