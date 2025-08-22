# monitoring/views.py
from collections import defaultdict
from django.db import transaction
from django.utils.timezone import now

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Host, Process
from .permissions import HasIngestApiKey
from .serializers import (
    HostReadSerializer,
    HostIngestSerializer,
    ProcessTreeReadSerializer,
)


# ---------- PUBLIC READ ENDPOINTS (for your HTML/JS) ----------

class HostListView(generics.ListAPIView):
    """
    GET /api/hosts/
    Lists all hosts with their system info (no processes).
    """
    queryset = Host.objects.all().order_by("hostname")
    serializer_class = HostReadSerializer


class HostDetailView(generics.RetrieveAPIView):
    """
    GET /api/hosts/<id>/
    Returns a single host with system info (no processes).
    """
    queryset = Host.objects.all()
    serializer_class = HostReadSerializer
    lookup_field = "id"


class HostProcessTreeView(APIView):
    """
    GET /api/hosts/<id>/processes/
    Returns only parent processes (parent is null) each with nested children.
    """
    def get(self, request, id):
        try:
            host = Host.objects.get(id=id)
        except Host.DoesNotExist:
            return Response({"detail": "Host not found."}, status=404)

        # Get top-level processes for this host
        parents = (
            Process.objects.filter(host=host, parent__isnull=True)
            .order_by("pid")
            .prefetch_related("children__children__children")  # shallow prefetch; recursion handled in serializer
        )
        data = ProcessTreeReadSerializer(parents, many=True).data
        return Response({
            "host": HostReadSerializer(host).data,
            "processes": data,
        })


# ---------- SECURE INGEST (agent → backend) ----------

class IngestView(APIView):
    """
    POST /api/ingest/
    Requires header: X-API-Key: <key>

    Body example:
    {
      "hostname": "DESKTOP-123",
      "operating_system": "Windows 11 Pro",
      "processor": "Intel Core i7-12700H",
      "num_cores": 8,
      "num_threads": 16,
      "ram_total": 17082165248,
      "ram_used": 9283647488,
      "ram_available": 7798517760,
      "storage_total": 512110190592,
      "storage_used": 301222969344,
      "storage_free": 210887221248,
      "processes": [
        {
          "pid": 1000,
          "name": "explorer.exe",
          "cpu": 1.2,
          "memory": 85.3,
          "children": [
            {"pid": 1200, "name": "dllhost.exe", "cpu": 0.2, "memory": 15.1}
          ]
        },
        ...
      ]
    }
    """
    permission_classes = [HasIngestApiKey]

    def post(self, request):
        serializer = HostIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        with transaction.atomic():
            # upsert host
            host, _created = Host.objects.get_or_create(
                hostname=payload["hostname"]
            )
            # update system info
            for f in [
                "operating_system", "processor", "num_cores", "num_threads",
                "ram_total", "ram_used", "ram_available",
                "storage_total", "storage_used", "storage_free",
            ]:
                if f in payload:
                    setattr(host, f, payload[f])
            host.last_updated = now()
            host.save()

            # Replace (snapshot) current processes for this host:
            Process.objects.filter(host=host).delete()

            # Build the tree recursively
            def create_process_tree(items, parent=None):
                for item in items:
                    children = item.pop("children", [])
                    proc = Process.objects.create(
                        host=host,
                        parent=parent,
                        pid=item["pid"],
                        name=item["name"],
                        cpu_usage=item.get("cpu_usage"),
                        memory_usage=item.get("memory_usage"),
                    )
                    if children:
                        create_process_tree(children, parent=proc)

            create_process_tree(payload["processes"], parent=None)

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
