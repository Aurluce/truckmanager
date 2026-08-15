import csv
import io
import zipfile
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Max
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from trucks.models import Truck
from trips.models import Trip
from loadings.models import Loading
from alerts.models import Alert
from measurements.models import WeightMeasurement,FuelMeasurement,GPSPosition
from dashboard.geocoding import reverse_geocode


def get_tco_summary(truck, fuel_cost=0):
    purchase_price = float(getattr(truck, 'purchase_price', 0) or 0)
    months = max(int(getattr(truck, 'tco_months', 0) or 0), 1)
    monthly_tco = purchase_price / months if purchase_price else 0
    total_tco = purchase_price + float(fuel_cost or 0)
    return {
        'purchase_price': purchase_price,
        'tco_months': months,
        'monthly_tco': monthly_tco,
        'total_tco': total_tco,
    }

def build_daily_data(truck, report_date):
    start=timezone.make_aware(__import__('datetime').datetime.combine(report_date,__import__('datetime').time.min))
    end=start+timedelta(days=1)
    trips=Trip.objects.filter(truck=truck,start_time__gte=start,start_time__lt=end)
    loads=Loading.objects.filter(trip__in=trips)
    alerts=Alert.objects.filter(truck=truck,triggered_at__gte=start,triggered_at__lt=end)
    distance=sum(t.total_distance_km for t in trips); fuel=sum(t.total_fuel_consumed_l for t in trips)
    weight=sum(x.weight_kg for x in loads); revenue=weight/1000*float(truck.revenue_per_ton or 0); fuel_cost=fuel*float(truck.cost_per_liter or 0)
    
    # Mesures du jour
    weight_measurements = WeightMeasurement.objects.filter(trip__in=trips).order_by('timestamp')
    fuel_measurements = FuelMeasurement.objects.filter(trip__in=trips).order_by('timestamp')
    gps_positions = GPSPosition.objects.filter(trip__in=trips).order_by('timestamp')
    
    # Statistiques des mesures
    avg_weight = weight_measurements.aggregate(a=Avg('calibrated_weight_kg'))['a'] or 0
    max_weight = weight_measurements.aggregate(m=Max('calibrated_weight_kg'))['m'] or 0
    avg_speed = fuel_measurements.aggregate(a=Avg('speed_kmh'))['a'] or 0
    max_speed = fuel_measurements.aggregate(m=Max('speed_kmh'))['m'] or 0
    avg_rpm = fuel_measurements.aggregate(a=Avg('engine_rpm'))['a'] or 0
    avg_load = fuel_measurements.aggregate(a=Avg('engine_load'))['a'] or 0
    
    # Arrêts du jour
    stops = []
    current = None
    for p in gps_positions:
        if p.is_stationary or p.is_abnormal_stop:
            if current is None:
                current = {'start': p, 'end': p, 'is_abnormal_stop': p.is_abnormal_stop}
            else:
                current['end'] = p
        else:
            if current is not None:
                stops.append(current)
                current = None
    if current is not None:
        stops.append(current)
    
    # Géocodage des arrêts
    stops_data = []
    for s in stops:
        place_name = reverse_geocode(s['start'].latitude, s['start'].longitude)
        stops_data.append({
            'start_time': s['start'].timestamp,
            'end_time': s['end'].timestamp,
            'is_abnormal_stop': s['is_abnormal_stop'],
            'place_name': place_name,
            'lat': s['start'].latitude,
            'lng': s['start'].longitude,
        })
    
    tco = get_tco_summary(truck, fuel_cost)
    return {'trips':trips,'loads':loads,'alerts':alerts,'distance':distance,'fuel':fuel,'weight':weight,'revenue':revenue,'fuel_cost':fuel_cost,
            'l100':fuel*100/distance if distance else 0,'lton':fuel/(weight/1000) if weight else 0,
            'weight_measurements':weight_measurements,'fuel_measurements':fuel_measurements,'gps_positions':gps_positions,
            'avg_weight':avg_weight,'max_weight':max_weight,'avg_speed':avg_speed,'max_speed':max_speed,
            'avg_rpm':avg_rpm,'avg_load':avg_load,'stops':stops_data,'tco':tco}


def build_report_rows_for_export(truck, report_date):
    d = build_daily_data(truck, report_date)
    return [
        ['Type', 'Valeur'],
        ['Camion', truck.truck_id],
        ['Date', report_date.isoformat()],
        ['Trajets', str(d['trips'].count())],
        ['Distance', f"{d['distance']:.2f} km"],
        ['Poids total', f"{d['weight']:.1f} kg"],
        ['Consommation', f"{d['fuel']:.2f} L"],
        ['L/100 km', f"{d['l100']:.2f}"],
        ['L/tonne', f"{d['lton']:.2f}"],
        ['Recette journalière', f"{d['revenue']:,.0f} FCFA"],
        ['Coût carburant', f"{d['fuel_cost']:,.0f} FCFA"],
        ['Prix d\'achat', f"{d['tco']['purchase_price']:,.0f} FCFA"],
        ['TCO mensuel', f"{d['tco']['monthly_tco']:,.0f} FCFA"],
        ['TCO sur la durée', f"{d['tco']['total_tco']:,.0f} FCFA"],
        ['Alertes', str(d['alerts'].count())],
    ]


def generate_daily_csv(truck, report_date):
    d = build_daily_data(truck, report_date)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Section', 'Valeur'])
    writer.writerow(['Camion', truck.truck_id])
    writer.writerow(['Date', report_date.isoformat()])
    writer.writerow(['Trajets', d['trips'].count()])
    writer.writerow(['Distance (km)', f"{d['distance']:.2f}"])
    writer.writerow(['Poids total (kg)', f"{d['weight']:.1f}"])
    writer.writerow(['Consommation (L)', f"{d['fuel']:.2f}"])
    writer.writerow(['L/100 km', f"{d['l100']:.2f}"])
    writer.writerow(['L/tonne', f"{d['lton']:.2f}"])
    writer.writerow(['Recette journalière (FCFA)', f"{d['revenue']:,.0f}"])
    writer.writerow(['Coût carburant (FCFA)', f"{d['fuel_cost']:,.0f}"])
    writer.writerow(['Prix d\'achat (FCFA)', f"{d['tco']['purchase_price']:,.0f}"])
    writer.writerow(['TCO mensuel (FCFA)', f"{d['tco']['monthly_tco']:,.0f}"])
    writer.writerow(['TCO sur la durée (FCFA)', f"{d['tco']['total_tco']:,.0f}"])
    writer.writerow(['Alertes', d['alerts'].count()])
    return output.getvalue().encode('utf-8')


def generate_daily_xlsx(truck, report_date):
    rows = build_report_rows_for_export(truck, report_date)
    sheet_rows = []
    for row in rows:
        sheet_rows.append('<Row>' + ''.join(f'<Cell><Data ss:Type="String">{value}</Data></Cell>' for value in row) + '</Row>')
    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheetData>
        {''.join(sheet_rows)}
      </sheetData>
    </worksheet>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
      <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
      <Default Extension="xml" ContentType="application/xml"/>
      <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
      <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
      <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
      <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
    </Types>'''
    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <sheets><sheet name="Rapport" sheetId="1" r:id="rId1"/></sheets>
    </workbook>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
      <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
    </Relationships>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>TruckManager</Application></Properties>'''
    core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>TruckManager</dc:creator><cp:lastModifiedBy>TruckManager</cp:lastModifiedBy></cp:coreProperties>'''
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationship></Relationships>')
        zf.writestr('docProps/app.xml', app)
        zf.writestr('docProps/core.xml', core)
        zf.writestr('xl/workbook.xml', workbook)
        zf.writestr('xl/_rels/workbook.xml.rels', rels)
        zf.writestr('xl/worksheets/sheet1.xml', xml)
    return buffer.getvalue()

def generate_daily_pdf(truck,report_date):
    d=build_daily_data(truck,report_date); buf=__import__('io').BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet()
    
    # Style personnalisé pour les titres de section
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        textColor=colors.HexColor('#0A1628'),
        spaceBefore=10*mm,
        spaceAfter=4*mm,
    )
    
    story=[Paragraph('TruckManager — Rapport journalier',styles['Title']),
        Paragraph(f'{truck.truck_id} · {truck.license_plate} · {report_date.strftime("%d/%m/%Y")}',styles['Normal']),Spacer(1,8*mm)]
    
    # === Résumé général ===
    rows=[['Indicateur','Valeur'],['Trajets',str(d['trips'].count())],['Distance',f"{d['distance']:.2f} km"],['Poids total',f"{d['weight']:.1f} kg"],
          ['Consommation',f"{d['fuel']:.2f} L"],['L/100 km',f"{d['l100']:.2f}"],['L/tonne',f"{d['lton']:.2f}"],['Recette',f"{d['revenue']:,.0f} FCFA"],['Coût carburant',f"{d['fuel_cost']:,.0f} FCFA"],
          ['Prix d\'achat',f"{d['tco']['purchase_price']:,.0f} FCFA"],['TCO mensuel',f"{d['tco']['monthly_tco']:,.0f} FCFA"],['TCO sur la durée',f"{d['tco']['total_tco']:,.0f} FCFA"],['Alertes',str(d['alerts'].count())]]
    t=Table(rows,colWidths=[75*mm,75*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0A1628')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),6)])); story += [t,Spacer(1,8*mm)]
    
    # === Statistiques des mesures ===
    story += [Paragraph('Statistiques des mesures',section_style)]
    stats_rows=[['Indicateur','Valeur'],['Poids moyen',f"{d['avg_weight']:.1f} kg"],['Poids max',f"{d['max_weight']:.1f} kg"],
                ['Vitesse moyenne',f"{d['avg_speed']:.1f} km/h"],['Vitesse max',f"{d['max_speed']:.1f} km/h"],
                ['Régime moyen',f"{d['avg_rpm']:.0f} RPM"],['Charge moteur moyenne',f"{d['avg_load']:.1f}%"]]
    st=Table(stats_rows,colWidths=[75*mm,75*mm]); st.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),6)])); story += [st,Spacer(1,8*mm)]
    
    # === Trajets du jour ===
    story += [Paragraph('Trajets du jour',section_style)]
    trip_rows=[['#','Départ','Arrivée','Distance','Carburant','Statut']]
    for i,tr in enumerate(d['trips'],1):
        trip_rows.append([str(i),tr.start_time.strftime('%H:%M') if tr.start_time else '—',
                         tr.end_time.strftime('%H:%M') if tr.end_time else '—',
                         f"{tr.total_distance_km:.1f} km",f"{tr.total_fuel_consumed_l:.1f} L",
                         tr.get_status_display()])
    tt=Table(trip_rows,colWidths=[10*mm,25*mm,25*mm,30*mm,25*mm,35*mm]); tt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5),('FONTSIZE',(0,0),(-1,-1),8)])); story += [tt,Spacer(1,8*mm)]
    
    # === Arrêts et stationnements ===
    story += [Paragraph('Arrêts & stationnements',section_style)]
    if d['stops']:
        stop_rows=[['#','Lieu','Début','Fin','Durée','Type']]
        for i,s in enumerate(d['stops'],1):
            duration = (s['end_time'] - s['start_time']).total_seconds() / 60
            dur_str = f"{int(duration//60)}h {int(duration%60)}min" if duration >= 60 else f"{int(duration)} min"
            stop_rows.append([str(i),s['place_name'] or f"{s['lat']:.5f}, {s['lng']:.5f}",
                             s['start_time'].strftime('%H:%M'),s['end_time'].strftime('%H:%M'),
                             dur_str,'Anormal' if s['is_abnormal_stop'] else 'Stationnement'])
        stp=Table(stop_rows,colWidths=[10*mm,45*mm,20*mm,20*mm,20*mm,35*mm]); stp.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5),('FONTSIZE',(0,0),(-1,-1),8)])); story += [stp,Spacer(1,8*mm)]
    else:
        story += [Paragraph('Aucun arrêt détecté.',styles['Normal']),Spacer(1,8*mm)]
    
    # === Chargements ===
    story += [Paragraph('Chargements',section_style)]
    loadrows=[['Produit','Poids','Validé']]+[[x.product_name,f'{x.weight_kg:.1f} kg','Oui' if x.is_validated else 'En attente'] for x in d['loads'][:30]]
    lt=Table(loadrows,colWidths=[85*mm,35*mm,30*mm]); lt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5)])); story += [lt,Spacer(1,8*mm)]
    
    # === Photos des chargements ===
    story += [Paragraph('Photos des chargements',section_style)]
    photos=[]
    for x in d['loads']:
        if x.photo and getattr(x.photo,'path',None) and __import__('os').path.exists(x.photo.path):
            try: photos.append([Paragraph(x.product_name,styles['Normal']),Image(x.photo.path,width=45*mm,height=30*mm)])
            except Exception: pass
    if photos:
        pt=Table(photos,colWidths=[80*mm,70*mm]); pt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')])); story += [pt,Spacer(1,8*mm)]
    else: story += [Paragraph('Aucune photo disponible.',styles['Normal']),Spacer(1,8*mm)]
    
    # === Alertes du jour ===
    story += [Paragraph('Alertes du jour',section_style)]
    arows=[['Heure','Type','Valeur','Statut']]+[[x.triggered_at.strftime('%H:%M'),x.get_alert_type_display(),str(x.actual_value),x.get_status_display()] for x in d['alerts'][:30]]
    at=Table(arows,colWidths=[25*mm,45*mm,35*mm,45*mm]); at.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5),('FONTSIZE',(0,0),(-1,-1),8)])); story += [at,Spacer(1,8*mm)]
    
    # === Mesures de poids ===
    story += [Paragraph('Mesures de poids',section_style)]
    wrows=[['Heure','Poids brut','Poids filtré','Poids calibré','Surcharge']]
    for m in d['weight_measurements'][:30]:
        wrows.append([m.timestamp.strftime('%H:%M:%S'),f"{m.raw_weight_kg:.1f} kg",f"{m.filtered_weight_kg:.1f} kg",f"{m.calibrated_weight_kg:.1f} kg",'Oui' if m.is_overloaded else 'Non'])
    wt=Table(wrows,colWidths=[25*mm,30*mm,30*mm,30*mm,25*mm]); wt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5),('FONTSIZE',(0,0),(-1,-1),8)])); story += [wt,Spacer(1,8*mm)]
    
    # === Mesures de carburant ===
    story += [Paragraph('Mesures de carburant',section_style)]
    frows=[['Heure','Niveau %','Litres','Vitesse','RPM','Charge %','Vol']]
    for m in d['fuel_measurements'][:30]:
        frows.append([m.timestamp.strftime('%H:%M:%S'),f"{m.fuel_level_percent:.1f}%",f"{m.fuel_level_liters:.1f} L",
                     f"{m.speed_kmh or 0:.0f} km/h",str(m.engine_rpm or 0),f"{m.engine_load or 0:.0f}%",
                     'Oui' if m.is_fuel_theft else 'Non'])
    ft=Table(frows,colWidths=[25*mm,20*mm,20*mm,25*mm,20*mm,20*mm,20*mm]); ft.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a2a4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),5),('FONTSIZE',(0,0),(-1,-1),7)])); story += [ft,Spacer(1,8*mm)]
    
    # === Signature ===
    story += [Spacer(1,8*mm),Paragraph(f'Signature numérique TruckManager · généré le {timezone.now().strftime("%d/%m/%Y %H:%M")}',styles['Normal'])]
    doc.build(story); buf.seek(0); return buf