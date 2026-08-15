# alerts/models.py
from django.db import models
from django.utils import timezone  # 👈 Ajouter cet import
from django.contrib.auth.models import User
from trucks.models import Truck
from trips.models import Trip

class Alert(models.Model):
    """Modèle représentant une alerte."""
    
    class AlertType(models.TextChoices):
        OVERLOAD = 'OVERLOAD', 'Surcharge'
        FUEL_THEFT = 'FUEL_THEFT', 'Vol carburant'
        ABNORMAL_STOP = 'ABNORMAL_STOP', 'Arrêt anormal'
        LOW_FUEL = 'LOW_FUEL', 'Niveau carburant bas'
        SPEEDING = 'SPEEDING', 'Excès de vitesse'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance requise'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        RESOLVED = 'RESOLVED', 'Résolu'
        IGNORED = 'IGNORED', 'Ignoré'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
    
    truck = models.ForeignKey(
        Truck,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name="Camion"
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts',
        verbose_name="Trajet"
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        verbose_name="Type d'alerte"
    )
    message = models.TextField(verbose_name="Message")
    
    threshold_value = models.FloatField(verbose_name="Valeur seuil")
    actual_value = models.FloatField(verbose_name="Valeur réelle")
    
    details = models.JSONField(default=dict, blank=True, verbose_name="Détails")
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        verbose_name="Résolu par"
    )
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Résolu à")
    resolution_notes = models.TextField(blank=True, verbose_name="Notes de résolution")
    
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Déclenchée à")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['truck', 'status', 'triggered_at']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.truck.truck_id} ({self.triggered_at.strftime('%H:%M')})"
    
    def resolve(self, user, notes=''):
        """Marque l'alerte comme résolue."""
        self.status = self.Status.RESOLVED
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()