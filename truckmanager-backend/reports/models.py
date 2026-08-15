# reports/models.py
from django.db import models
from trucks.models import Truck

class Report(models.Model):
    """Modèle représentant un rapport journalier."""
    
    truck = models.ForeignKey(
        Truck,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Camion"
    )
    
    # Période
    report_date = models.DateField(verbose_name="Date du rapport")
    
    # Résumé des trajets
    total_trips = models.IntegerField(default=0, verbose_name="Nombre de trajets")
    total_distance_km = models.FloatField(default=0, verbose_name="Distance totale (km)")
    total_duration_hours = models.FloatField(default=0, verbose_name="Durée totale (h)")
    
    # Poids
    total_weight_kg = models.FloatField(default=0, verbose_name="Poids total transporté (kg)")
    avg_weight_kg = models.FloatField(default=0, verbose_name="Poids moyen (kg)")
    
    # Carburant
    total_fuel_consumed_l = models.FloatField(default=0, verbose_name="Consommation totale (L)")
    avg_fuel_consumption_l_100km = models.FloatField(default=0, verbose_name="Consommation moyenne (L/100km)")
    avg_fuel_per_ton_km = models.FloatField(default=0, verbose_name="Consommation par tonne (L/tonne)")
    
    # Financier
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Recette totale"
    )
    total_fuel_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Coût carburant"
    )
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Marge (%)"
    )
    
    # Alertes
    total_alerts = models.IntegerField(default=0, verbose_name="Nombre d'alertes")
    resolved_alerts = models.IntegerField(default=0, verbose_name="Alertes résolues")
    
    # Fichier PDF
    pdf_file = models.FileField(
        upload_to='reports/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Fichier PDF"
    )
    pdf_generated_at = models.DateTimeField(null=True, blank=True, verbose_name="PDF généré à")
    signature_hash = models.CharField(max_length=64, blank=True, default='', verbose_name='Signature numérique')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-report_date']
        unique_together = ['truck', 'report_date']
    
    def __str__(self):
        return f"Rapport {self.truck.truck_id} - {self.report_date}"