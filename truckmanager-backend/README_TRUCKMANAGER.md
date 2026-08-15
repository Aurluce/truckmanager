# TruckManager — intégration ESP32 / Dashboard

## Données ESP32
Authentification firmware par `X-API-Key` + `X-Device-ID`.

Endpoint principal:
`POST /api/v1/donnees/telemetry/`

Exemple:
```json
{
  "timestamp": "2026-08-09T08:30:00Z",
  "poids_kg": 2450.3,
  "carburant_pct": 67.2,
  "rpm": 1850,
  "charge_moteur": 42,
  "gps": {"lat": 3.8480, "lng": 11.5021, "vitesse_kmh": 62},
  "alertes": [],
  "camion_id": "ESP32-001"
}
```

Endpoints spécialisés:
- `POST /api/v1/donnees/poids/`
- `POST /api/v1/donnees/carburant/`
- `POST /api/v1/donnees/gps/`
- `POST /api/v1/donnees/alertes/`

Le backend associe automatiquement la trame au camion via la clé API, crée un trajet si nécessaire, enregistre les mesures et déclenche les alertes selon la configuration du camion.

## Dashboard
- `/api/v1/dashboard/summary/`
- `/api/v1/dashboard/fleet/`
- `/api/v1/dashboard/series/`
- `/api/v1/dashboard/live/<truck_id>/`
- `/api/v1/dashboard/alerts/`
- `/api/v1/dashboard/loads/`

## Rapport
- `GET /api/v1/reports/daily_pdf/?truck_id=<id>&date=YYYY-MM-DD`
- `POST /api/v1/reports/generate/`
- `python manage.py generate_daily_reports`

Pour l'automatisation à 23h59, planifier la commande avec cron:
`59 23 * * * /chemin/venv/bin/python /chemin/backend/manage.py generate_daily_reports`

## Installation
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```
