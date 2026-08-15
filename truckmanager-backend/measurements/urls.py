from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeightMeasurementViewSet, FuelMeasurementViewSet, GPSPositionViewSet

router = DefaultRouter()
router.register(r'weight', WeightMeasurementViewSet, basename='weight')
router.register(r'fuel', FuelMeasurementViewSet, basename='fuel')
router.register(r'gps', GPSPositionViewSet, basename='gps')

urlpatterns = [
    path('', include(router.urls)),
]
