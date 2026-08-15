from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoadingViewSet

router = DefaultRouter()
router.register(r'loadings', LoadingViewSet, basename='loading')

urlpatterns = [
    path('', include(router.urls)),
]
