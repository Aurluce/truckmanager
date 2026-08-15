from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer, AlertListSerializer
from core.permissions import IsManager
from core.models import get_user_role

class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des alertes.
    - GET /api/alerts/ : Liste des alertes
    - POST /api/alerts/ : Créer une alerte (firmware)
    - GET /api/alerts/{id}/ : Détails d'une alerte
    - PUT /api/alerts/{id}/ : Modifier une alerte
    - DELETE /api/alerts/{id}/ : Supprimer une alerte
    """
    
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'status', 'truck', 'truck__owner']
    search_fields = ['message', 'truck__truck_id']
    ordering_fields = ['triggered_at', 'status']
    ordering = ['-triggered_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Alert.objects.all()
        user_role = get_user_role(user)
        if not user.is_superuser and user_role != 'ADMIN':
            queryset = queryset.filter(truck__owner=user)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Marque une alerte comme résolue."""
        alert = self.get_object()
        if alert.status == 'RESOLVED':
            return Response(
                {'error': 'Cette alerte est déjà résolue.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.resolve(request.user, request.data.get('notes', ''))
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """Ignore une alerte."""
        alert = self.get_object()
        alert.status = 'IGNORED'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', 'Ignoré')
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des alertes."""
        from dashboard.services import DashboardService
        truck_id = request.query_params.get('truck_id')
        data = DashboardService.get_alerts_summary(truck_id)
        return Response(data)
