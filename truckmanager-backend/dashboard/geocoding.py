# dashboard/geocoding.py
"""Utilitaire de géocodage inverse pour déterminer le nom d'un lieu à partir de coordonnées GPS."""
import time
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

logger = logging.getLogger(__name__)

# Cache simple en mémoire pour éviter les appels répétés
_cache = {}
_CACHE_TTL = 3600  # 1 heure
_last_request_time = 0

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

def reverse_geocode(lat, lng, timeout=3):
    """
    Détermine le nom d'un lieu à partir de coordonnées GPS.
    Retourne un nom lisible ou None si le géocodage échoue.
    """
    global _last_request_time
    
    if lat is None or lng is None:
        return None
    
    # Arrondir pour le cache (précision ~100m)
    key = (round(lat, 3), round(lng, 3))
    
    # Vérifier le cache
    if key in _cache:
        cached = _cache[key]
        if time.time() - cached['time'] < _CACHE_TTL:
            return cached['name']
    
    # Respecter la limite de 1 requête/seconde de Nominatim
    elapsed = time.time() - _last_request_time
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    
    try:
        params = urlencode({
            'lat': str(lat),
            'lon': str(lng),
            'format': 'json',
            'zoom': 16,
            'addressdetails': 1,
        })
        req = Request(f"{NOMINATIM_URL}?{params}", headers={
            'User-Agent': 'TruckManager/1.0 (fleet management system)',
        })
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        _last_request_time = time.time()
        
        # Construire un nom lisible
        name = _build_place_name(data)
        
        # Mettre en cache
        _cache[key] = {'name': name, 'time': time.time()}
        return name
    except Exception as e:
        logger.warning(f"Géocodage inverse échoué pour ({lat}, {lng}): {e}")
        _last_request_time = time.time()
        return None

def _build_place_name(data):
    """Construit un nom de lieu lisible à partir de la réponse Nominatim."""
    if not data:
        return None
    
    address = data.get('address', {})
    display_name = data.get('display_name', '')
    
    # Priorité aux noms spécifiques
    parts = []
    for key in ['road', 'pedestrian', 'footway', 'path', 'neighbourhood', 'suburb', 'village', 'town', 'city']:
        if address.get(key):
            parts.append(address[key])
            break
    
    # Ajouter la région/commune
    for key in ['county', 'state', 'region', 'municipality']:
        if address.get(key) and address[key] not in parts:
            parts.append(address[key])
            break
    
    if parts:
        return ', '.join(parts)
    
    # Fallback : utiliser le display_name tronqué
    if display_name:
        return display_name.split(',')[0]
    
    return None

def batch_reverse_geocode(points):
    """
    Géocode une liste de points (lat, lng) en série avec cache.
    Retourne un dict {(lat, lng): nom}.
    """
    results = {}
    for lat, lng in points:
        if lat is None or lng is None:
            continue
        name = reverse_geocode(lat, lng)
        if name:
            results[(round(lat, 3), round(lng, 3))] = name
    return results