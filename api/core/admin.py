# monitoring/admin.py
from django.contrib import admin
from .models import Host, Process, ApiKey

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("hostname", "operating_system", "processor", "last_updated")
    search_fields = ("hostname", "operating_system", "processor")

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("host", "pid", "name", "parent", "cpu_usage", "memory_usage", "created_at")
    list_filter = ("host",)
    search_fields = ("name", "pid")

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "key")
