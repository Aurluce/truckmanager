from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Loading
from .serializers import LoadingSerializer, LoadingListSerializer
from core.permissions import IsManager, IsOwnerOrReadOnly
from core.models import get_user_role

class LoadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des chargements.
    - GET /api/loadings/ : Liste des chargements
    - POST /api/loadings/ : Créer un chargement
    - GET /api/loadings/{id}/ : Détails d'un chargement
    - PUT /api/loadings/{id}/ : Modifier un chargement
    - DELETE /api/loadings/{id}/ : Supprimer un chargement
    """
    
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip', 'is_validated', 'trip__truck', 'trip__truck__owner']
    search_fields = ['product_name', 'product_type', 'trip__truck__truck_id']
    ordering_fields = ['created_at', 'weight_kg']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Loading.objects.all()
        user_role = get_user_role(user)
        if not user.is_superuser and user_role != 'ADMIN':
            queryset = queryset.filter(trip__truck__owner=user)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LoadingListSerializer
        return LoadingSerializer
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valide un chargement."""
        loading = self.get_object()
        if loading.is_validated:
            return Response(
                {'error': 'Ce chargement est déjà validé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loading.is_validated = True
        loading.validated_by = request.user
        loading.validated_at = timezone.now()
        loading.save()
        
        serializer = self.get_serializer(loading)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Récupère les chargements en cours."""
        user = request.user
        queryset = Loading.objects.filter(trip__status='IN_PROGRESS')
        user_role = get_user_role(user)
        if not user.is_superuser and user_role != 'ADMIN':
            queryset = queryset.filter(trip__truck__owner=user)
        serializer = LoadingListSerializer(queryset, many=True)
        return Response(serializer.data)
