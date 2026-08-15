from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/daily_pdf/', ReportViewSet.as_view({'get': 'daily_pdf'}), name='report-daily-pdf'),
    path('reports/daily_export/', ReportViewSet.as_view({'get': 'daily_export'}), name='report-daily-export'),
]
