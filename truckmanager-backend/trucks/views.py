import secrets
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Truck
from .serializers import TruckSerializer, TruckListSerializer
from core.permissions import IsManager

class TruckViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated, IsManager]
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['owner','is_active']
    search_fields=['truck_id','license_plate','brand','model','esp32_device_id']
    ordering_fields=['created_at','truck_id','license_plate']
    ordering=['-created_at']
    def get_queryset(self):
        from core.models import get_user_role
        qs=Truck.objects.select_related('owner')
        user_role = get_user_role(self.request.user)
        if not self.request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(owner=self.request.user)
        return qs
    def get_serializer_class(self): return TruckListSerializer if self.action=='list' else TruckSerializer
    def perform_create(self,serializer):
        owner=self.request.user if not self.request.user.is_superuser else serializer.validated_data.get('owner',self.request.user)
        serializer.save(owner=owner)
    @action(detail=True,methods=['post'])
    def rotate_api_key(self,request,pk=None):
        truck=self.get_object()
        truck.api_key=secrets.token_urlsafe(32)
        truck.save(update_fields=['api_key','updated_at'])
        return Response({'truck_id':truck.truck_id,'api_key':truck.api_key})
    @action(detail=True,methods=['get'])
    def live(self,request,pk=None):
        from dashboard.services import DashboardService
        return Response(DashboardService.get_realtime_data(self.get_object().id))
    @action(detail=True,methods=['get'])
    def report(self,request,pk=None):
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER
        from io import BytesIO

        truck=self.get_object()
        owner_name=truck.owner.get_full_name() or truck.owner.username
        driver_name=truck.driver.get_full_name() if truck.driver else None

        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=20*mm,bottomMargin=20*mm)

        styles=getSampleStyleSheet()
        title_style=ParagraphStyle('TitleCustom',parent=styles['Title'],textColor=colors.HexColor('#0891b2'),spaceAfter=6)
        h2_style=ParagraphStyle('H2Custom',parent=styles['Heading2'],textColor=colors.HexColor('#0e7490'),spaceBefore=18,spaceAfter=8)
        info_style=ParagraphStyle('InfoBox',parent=styles['Normal'],backColor=colors.HexColor('#f0f9ff'),borderColor=colors.HexColor('#0891b2'),borderWidth=1,borderPadding=8,spaceAfter=12)
        footer_style=ParagraphStyle('Footer',parent=styles['Normal'],alignment=TA_CENTER,textColor=colors.grey,fontSize=9,spaceBefore=30)

        def build_table(rows):
            data=[['Propriété','Valeur']]+rows
            t=Table(data,colWidths=[70*mm,100*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0891b2')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('BOTTOMPADDING',(0,0),(-1,-1),8),
                ('TOPPADDING',(0,0),(-1,-1),8),
                ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f8fafc')]),
            ]))
            return t

        elements=[]
        elements.append(Paragraph('Rapport de Camion',title_style))
        elements.append(Paragraph(
            f"<b>Généré le:</b> {truck.updated_at.strftime('%d/%m/%Y %H:%M')}<br/>"
            f"<b>ID Camion:</b> {truck.truck_id}",
            info_style
        ))

        elements.append(Paragraph('Informations Générales',h2_style))
        general_rows=[
            ['ID Camion',truck.truck_id],
            ['Plaque d\'immatriculation',truck.license_plate],
            ['Marque',truck.brand],
            ['Modèle',truck.model],
            ['Année',str(truck.year)],
            ['Statut','Actif' if truck.is_active else 'Inactif'],
            ['Propriétaire',owner_name],
        ]
        if driver_name:
            general_rows.append(['Conducteur',driver_name])
        elements.append(build_table(general_rows))

        elements.append(Paragraph('Spécifications Techniques',h2_style))
        elements.append(build_table([
            ['Capacité maximale',f"{truck.max_capacity_kg} kg"],
            ['Capacité du réservoir',f"{truck.fuel_tank_capacity_l} L"],
            ['Seuil surcharge',f"{truck.overload_threshold_kg} kg"],
            ['Seuil vol carburant',f"{truck.fuel_theft_threshold_l} L"],
            ['Arrêt anormal',f"{truck.abnormal_stop_minutes} min"],
            ['Seuil carburant bas',f"{truck.low_fuel_threshold_percent}%"],
            ['Limite vitesse',f"{truck.speed_limit_kmh} km/h"],
        ]))

        elements.append(Paragraph('Paramètres Financiers',h2_style))
        elements.append(build_table([
            ['Coût par km',f"{truck.cost_per_km} FCFA"],
            ['Coût par litre',f"{truck.cost_per_liter} FCFA"],
            ['Revenu par tonne',f"{truck.revenue_per_ton} FCFA"],
        ]))

        elements.append(Paragraph('Équipement ESP32',h2_style))
        elements.append(build_table([
            ['ID ESP32',truck.esp32_device_id or 'Non configuré'],
            ['Adresse MAC',truck.esp32_mac_address or 'Non configuré'],
            ['Version firmware',truck.firmware_version or 'N/A'],
        ]))

        elements.append(Spacer(1,20))
        elements.append(Paragraph('TruckManager - Système de Gestion de Flotte<br/>Document généré automatiquement',footer_style))

        doc.build(elements)
        pdf=buffer.getvalue()
        buffer.close()

        response=HttpResponse(content_type='application/pdf')
        response['Content-Disposition']=f'attachment; filename="rapport_{truck.truck_id}.pdf"'
        response.write(pdf)
        return response
