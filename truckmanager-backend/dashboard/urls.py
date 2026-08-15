from django.urls import path
from .views import DashboardSummaryView,RealtimeDataView,FleetMapView,DashboardSeriesView,DashboardAlertsView,DashboardLoadsView
from .ingestion import DeviceTelemetryView,DeviceWeightView,DeviceFuelView,DeviceGPSView,DeviceAlertView
urlpatterns=[
 path('summary/',DashboardSummaryView.as_view()),path('live/<int:truck_id>/',RealtimeDataView.as_view()),
 path('fleet/',FleetMapView.as_view()),path('series/',DashboardSeriesView.as_view()),
 path('alerts/',DashboardAlertsView.as_view()),path('loads/',DashboardLoadsView.as_view()),
 path('telemetry/',DeviceTelemetryView.as_view()),path('poids/',DeviceWeightView.as_view()),
 path('carburant/',DeviceFuelView.as_view()),path('gps/',DeviceGPSView.as_view()),path('alertes/',DeviceAlertView.as_view()),
]
