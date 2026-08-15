from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from measurements.views import FuelMeasurementViewSet
from dashboard.ingestion import DeviceTelemetryView,DeviceWeightView,DeviceFuelView,DeviceGPSView,DeviceAlertView,DeviceLoadingView
schema_view=get_schema_view(openapi.Info(title='TruckManager API',default_version='v1',description='API de suivi de flotte'),public=True,permission_classes=(permissions.AllowAny,))
urlpatterns=[
 path('admin/',admin.site.urls),
 path('swagger/',schema_view.with_ui('swagger',cache_timeout=0)),
 path('redoc/',schema_view.with_ui('redoc',cache_timeout=0)),
 path('swagger.json',schema_view.without_ui(cache_timeout=0)),
 path('api/v1/auth/',include('core.urls')),
 path('api/v1/',include('trucks.urls')),
 path('api/v1/',include('trips.urls')),
 path('api/v1/',include('measurements.urls')),
 path('api/v1/',include('alerts.urls')),
 path('api/v1/',include('loadings.urls')),
 path('api/v1/',include('reports.urls')),
 path('api/v1/dashboard/',include('dashboard.urls')),
 path('api/v1/donnees/',include('dashboard.urls')),
 path('api/v1/carburant/live/',FuelMeasurementViewSet.as_view({'get':'live'})),
 path('api/v1/carburant/historique/',FuelMeasurementViewSet.as_view({'get':'historique'})),
 path('api/v1/positions/',DeviceGPSView.as_view()),
 path('api/v1/chargements/',DeviceLoadingView.as_view()),
 path('api/v1/alertes/',DeviceAlertView.as_view()),
]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
