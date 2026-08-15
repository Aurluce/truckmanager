# dashboard/utils.py
import io
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.http import HttpResponse
from django.utils import timezone
from .services import DashboardService

def generate_pdf_report(truck_id, period='month'):
    """Génère un rapport PDF complet."""
    # Récupérer les données
    stats = {
        'trucks': DashboardService.get_truck_stats(truck_id),
        'trips': DashboardService.get_trips_stats(truck_id),
        'alerts': DashboardService.get_alerts_summary(truck_id),
        'financial': DashboardService.get_financial_stats(truck_id),
    }
    
    # Créer le PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.HexColor('#0A1628')
    )
    story.append(Paragraph('TruckManager - Rapport de Performance', title_style))
    story.append(Paragraph(f'Date: {timezone.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Statistiques des camions
    story.append(Paragraph('Statistiques de la Flotte', styles['Heading2']))
    truck_data = [
        ['Indicateur', 'Valeur'],
        ['Total camions', str(stats['trucks']['total_trucks'])],
        ['Camions actifs', str(stats['trucks']['active_trucks'])],
        ['Camions en trajet', str(stats['trucks']['in_trip'])],
        ['Camions à l\'arrêt', str(stats['trucks']['idle'])],
    ]
    truck_table = Table(truck_data)
    truck_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(truck_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Statistiques des trajets
    story.append(Paragraph('Statistiques des Trajets', styles['Heading2']))
    trip_data = [
        ['Indicateur', 'Valeur'],
        ['Total trajets', str(stats['trips']['total_trips'])],
        ['Trajets terminés', str(stats['trips']['completed'])],
        ['Trajets en cours', str(stats['trips']['in_progress'])],
        ['Distance totale', f"{stats['trips']['total_distance_km']} km"],
        ['Consommation totale', f"{stats['trips']['total_fuel_l']} L"],
    ]
    trip_table = Table(trip_data)
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(trip_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Alertes
    story.append(Paragraph('Résumé des Alertes', styles['Heading2']))
    alert_data = [
        ['Indicateur', 'Valeur'],
        ['Total alertes', str(stats['alerts']['total_alerts'])],
        ['Alertes en attente', str(stats['alerts']['pending'])],
        ['Alertes résolues', str(stats['alerts']['resolved'])],
    ]
    alert_table = Table(alert_data)
    alert_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(alert_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Financier
    story.append(Paragraph('Statistiques Financières', styles['Heading2']))
    fin_data = [
        ['Indicateur', 'Valeur (FCFA)'],
        ['Coût total', f"{stats['financial']['total_cost_fcfa']:,.0f}"],
        ['Revenu total', f"{stats['financial']['total_revenue_fcfa']:,.0f}"],
        ['Bénéfice', f"{stats['financial']['profit_fcfa']:,.0f}"],
        ['Marge bénéficiaire', f"{stats['financial']['profit_margin']}%"],
    ]
    fin_table = Table(fin_data)
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(fin_table)
    
    # Pied de page
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph('TruckManager - Gestion de Flotte Intelligente', styles['Normal']))
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_excel_report(data, filename='report.xlsx'):
    """Génère un rapport Excel."""
    # À implémenter avec openpyxl ou xlsxwriter
    pass