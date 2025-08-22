# monitoring/models.py
from django.db import models


class ApiKey(models.Model):
    """Simple API key for agent authentication."""
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=64, unique=True)  # store a random 32/64 hex string
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"


class Host(models.Model):
    """Represents a machine that reports system info."""
    hostname = models.CharField(max_length=255, unique=True)

    # System details
    operating_system = models.CharField(max_length=255, blank=True, default="")
    processor = models.CharField(max_length=255, blank=True, default="")
    num_cores = models.IntegerField(default=0)
    num_threads = models.IntegerField(default=0)

    # RAM (bytes)
    ram_total = models.BigIntegerField(default=0)
    ram_used = models.BigIntegerField(default=0)
    ram_available = models.BigIntegerField(default=0)

    # Storage (bytes, for total of all volumes or main volume)
    storage_total = models.BigIntegerField(default=0)
    storage_used = models.BigIntegerField(default=0)
    storage_free = models.BigIntegerField(default=0)

    # When this host last ingested a report
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hostname


class Process(models.Model):
    """
    A process running on a host.
    Parent-child relationship modeled with self FK.
    """
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="processes")

    pid = models.IntegerField()  # process id on the host
    name = models.CharField(max_length=255)
    cpu_usage = models.FloatField(null=True, blank=True, help_text="percent")
    memory_usage = models.FloatField(null=True, blank=True, help_text="MB")

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["host", "pid"]),
        ]
        unique_together = (("host", "pid"),)

    def __str__(self):
        return f"{self.name} (PID {self.pid}) on {self.host.hostname}"
