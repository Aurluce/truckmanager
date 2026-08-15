# loadings/models.py
from django.db import models
from trucks.models import Truck
from trips.models import Trip
from django.contrib.auth.models import User

class Loading(models.Model):
    """Modèle représentant un chargement."""
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='loadings',
        verbose_name="Trajet"
    )
    
    # Produit
    product_name = models.CharField(max_length=255, verbose_name="Nom du produit")
    product_type = models.CharField(max_length=100, blank=True, verbose_name="Type de produit")
    
    # Poids
    weight_kg = models.FloatField(verbose_name="Poids (kg)")
    weight_verified = models.BooleanField(default=False, verbose_name="Poids vérifié")
    
    # Photo
    photo = models.ImageField(
        upload_to='loadings/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    photo_taken_at = models.DateTimeField(null=True, blank=True, verbose_name="Photo prise à")
    
    # Validation
    is_validated = models.BooleanField(default=False, verbose_name="Validation propriétaire")
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_loadings',
        verbose_name="Validé par"
    )
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name="Validé à")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Chargement"
        verbose_name_plural = "Chargements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.weight_kg}kg ({self.trip.truck.truck_id})"