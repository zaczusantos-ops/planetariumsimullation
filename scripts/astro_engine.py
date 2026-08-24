"""
Mecanismo de Projeção Astronômica Real (Base HYG 3.8)
Converte coordenadas equatoriais reais (RA, Dec, Mag, Spect) em coordenadas horizontais (Alt, Az, X, Y, Z).
"""

import csv
import math
import os

def load_real_stars(catalog_path="data/hyg.csv", max_mag=6.0):
    stars = []
    if not os.path.exists(catalog_path):
        return stars

    with open(catalog_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['mag'] or not row['ra'] or not row['dec']:
                continue
            mag = float(row['mag'])
            if mag <= max_mag and row['proper'] != 'Sol':
                ra_hours = float(row['ra'])
                dec_deg = float(row['dec'])
                spect = row.get('spect', '')
                proper = row.get('proper', '')
                bayer = row.get('bayer', '')
                con = row.get('con', '')
                ci = float(row['ci']) if row.get('ci') else 0.5
                
                stars.append({
                    'ra_rad': math.radians(ra_hours * 15.0), # 1h = 15°
                    'dec_rad': math.radians(dec_deg),
                    'mag': mag,
                    'spect': spect,
                    'proper': proper,
                    'bayer': bayer,
                    'con': con,
                    'ci': ci
                })
    return stars

def equatorial_to_horizontal(ra_rad, dec_rad, lat_rad, lst_rad):
    """
    Converte (RA, Dec) para (Altitude, Azimute medido de Norte para Leste 0-360°).
    """
    # Ângulo horário: H = LST - RA
    H = lst_rad - ra_rad
    
    sin_alt = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(H)
    alt_rad = math.asin(max(-1.0, min(1.0, sin_alt)))
    
    y = -math.cos(dec_rad) * math.sin(H)
    x = math.sin(dec_rad) * math.cos(lat_rad) - math.cos(dec_rad) * math.sin(lat_rad) * math.cos(H)
    az_rad = math.atan2(y, x)
    if az_rad < 0:
        az_rad += 2 * math.pi
        
    return alt_rad, az_rad

def star_color_from_spect(spect, ci):
    """
    Retorna RGBA baseado na classe espectral real.
    """
    if spect.startswith('O') or spect.startswith('B'):
        return (0.75, 0.85, 1.0, 1.0) # Azulado quente
    elif spect.startswith('A'):
        return (0.95, 0.98, 1.0, 1.0) # Branco puro
    elif spect.startswith('F'):
        return (1.0, 1.0, 0.95, 1.0)  # Branco-amarelado
    elif spect.startswith('G'):
        return (1.0, 0.95, 0.7, 1.0)  # Amarelo (tipo Sol)
    elif spect.startswith('K'):
        return (1.0, 0.75, 0.45, 1.0) # Laranja
    elif spect.startswith('M'):
        return (1.0, 0.5, 0.3, 1.0)   # Vermelho
    else:
        return (0.9, 0.95, 1.0, 1.0)
