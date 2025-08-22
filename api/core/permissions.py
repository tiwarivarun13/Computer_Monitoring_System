# monitoring/permissions.py
from rest_framework.permissions import BasePermission
from .models import ApiKey

class HasIngestApiKey(BasePermission):
    """
    Allow only if request has header X-API-Key that matches an active ApiKey.
    """

    def has_permission(self, request, view):
        api_key = request.headers.get("X-API-Key") or request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return False
        return ApiKey.objects.filter(key=api_key, is_active=True).exists()
