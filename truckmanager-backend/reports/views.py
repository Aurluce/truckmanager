from rest_framework import viewsets,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.utils import timezone
import hashlib
from .models import Report
from .serializers import ReportSerializer,ReportListSerializer
from .services import generate_daily_pdf, build_daily_data, generate_daily_csv, generate_daily_xlsx
from trucks.models import Truck
from core.models import get_user_role
class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields=['truck','report_date']
    ordering=['-report_date']
    def get_queryset(self):
        qs=Report.objects.select_related('truck')
        user_role = get_user_role(self.request.user)
        if not self.request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(truck__owner=self.request.user)
        return qs
    def get_serializer_class(self): return ReportListSerializer if self.action=='list' else ReportSerializer
    @action(detail=False,methods=['get'])
    def daily_pdf(self,request):
        truck_id=request.query_params.get('truck_id')
        report_date=request.query_params.get('date')
        from datetime import date
        d=date.fromisoformat(report_date) if report_date else timezone.localdate()
        user_role = get_user_role(request.user)
        qs=Truck.objects.all() if request.user.is_superuser or user_role == 'ADMIN' else Truck.objects.filter(owner=request.user)
        truck=qs.filter(id=truck_id).first() if truck_id else qs.first()
        if not truck: return Response({'error':'Aucun camion'},404)
        pdf=generate_daily_pdf(truck,d); r=HttpResponse(pdf,content_type='application/pdf'); r['Content-Disposition']=f'attachment; filename="truckmanager_{truck.truck_id}_{d}.pdf"'; return r

    @action(detail=False, methods=['get'])
    def daily_export(self, request):
        truck_id = request.query_params.get('truck_id')
        report_date = request.query_params.get('date')
        export_format = request.query_params.get('format', 'csv').lower()
        from datetime import date
        d = date.fromisoformat(report_date) if report_date else timezone.localdate()
        user_role = get_user_role(request.user)
        qs = Truck.objects.all() if request.user.is_superuser or user_role == 'ADMIN' else Truck.objects.filter(owner=request.user)
        truck = qs.filter(id=truck_id).first() if truck_id else qs.first()
        if not truck:
            return Response({'error': 'Aucun camion'}, status=404)

        if export_format == 'xlsx':
            content = generate_daily_xlsx(truck, d)
            response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="truckmanager_{truck.truck_id}_{d}.xlsx"'
            return response

        content = generate_daily_csv(truck, d)
        response = HttpResponse(content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="truckmanager_{truck.truck_id}_{d}.csv"'
        return response
    @action(detail=False,methods=['post'])
    def generate(self,request):
        from datetime import date
        d=date.fromisoformat(str(request.data.get('report_date',timezone.localdate())))
        user_role = get_user_role(request.user)
        trucks=Truck.objects.filter(id=request.data.get('truck_id')) if request.data.get('truck_id') else (Truck.objects.all() if request.user.is_superuser or user_role == 'ADMIN' else Truck.objects.filter(owner=request.user))
        created=[]
        for truck in trucks:
            data=build_daily_data(truck,d)
            signature=hashlib.sha256(f'{truck.truck_id}|{d.isoformat()}|{data["distance"]:.3f}|{data["fuel"]:.3f}|{data["weight"]:.3f}'.encode()).hexdigest()
            # Calculer la durée totale des trajets
            total_duration = sum(
                ((t.end_time - t.start_time).total_seconds() / 3600) 
                for t in data['trips'] if t.end_time and t.start_time
            )
            # Marge bénéficiaire
            profit_margin = ((data['revenue'] - data['fuel_cost']) / data['revenue'] * 100) if data['revenue'] else 0
            report, _=Report.objects.update_or_create(truck=truck,report_date=d,defaults={
                'total_trips':data['trips'].count(),
                'total_distance_km':data['distance'],
                'total_duration_hours':round(total_duration, 2),
                'total_weight_kg':data['weight'],
                'avg_weight_kg':round(data['avg_weight'], 2),
                'total_fuel_consumed_l':data['fuel'],
                'avg_fuel_consumption_l_100km':data['l100'],
                'avg_fuel_per_ton_km':data['lton'],
                'total_revenue':data['revenue'],
                'total_fuel_cost':data['fuel_cost'],
                'profit_margin':round(profit_margin, 2),
                'total_alerts':data['alerts'].count(),
                'resolved_alerts':data['alerts'].filter(status='RESOLVED').count(),
                'signature_hash':signature,
                'pdf_generated_at':timezone.now()
            })
            created.append(report.id)
        return Response({'created':created})
