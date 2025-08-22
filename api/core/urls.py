# monitoring/urls.py
from django.urls import path
from .views import (
    HostListView,
    HostDetailView,
    HostProcessTreeView,
    IngestView,
)

urlpatterns = [
    # public (frontend)
    path("hosts/", HostListView.as_view(), name="host-list"),
    path("hosts/<int:id>/", HostDetailView.as_view(), name="host-detail"),
    path("hosts/<int:id>/processes/", HostProcessTreeView.as_view(), name="host-processes"),

    # secure ingest (agent)
    path("ingest/", IngestView.as_view(), name="ingest"),
]
