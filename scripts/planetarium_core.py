"""
Planetarium Core Engine - Mecanismo Universal de Planetário Astronômico
Utiliza o catálogo estelar real HYG 3.8 (Hipparcos + Yale + Gliese) e catálogo Messier.
Suporta controle de poluição luminosa (magnitude limite / escala de Bortle).
"""

import bpy
import csv
import json
import math
import numpy as np
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

def load_messier_objects(messier_path="data/astronomy/messier.json"):
    if not os.path.exists(messier_path):
        return []
    with open(messier_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('features', [])

def equatorial_to_horizontal(ra_rad, dec_rad, lat_rad, lst_rad):
    """
    Converte (RA, Dec) para (Altitude, Azimute medido de Norte para Leste 0-360°).
    """
    H = lst_rad - ra_rad
    sin_alt = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(H)
    alt_rad = math.asin(max(-1.0, min(1.0, sin_alt)))
    
    y = -math.cos(dec_rad) * math.sin(H)
    x = math.sin(dec_rad) * math.cos(lat_rad) - math.cos(dec_rad) * math.sin(lat_rad) * math.cos(H)
    az_rad = math.atan2(y, x)
    if az_rad < 0:
        az_rad += 2 * math.pi
        
    return alt_rad, az_rad

def create_emission_mat(name, color, strength=5.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    emit = nodes.new(type='ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = strength
    mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def setup_vr_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 1024
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 30

    scene.render.image_settings.media_type = 'IMAGE'
    scene.render.image_settings.file_format = 'PNG'
    
    # Câmera 360 Panorâmica Equiretangular
    cam_data = bpy.data.cameras.new("VR_Camera_360")
    cam_data.type = 'PANO'
    cam_data.panorama_type = 'EQUIRECTANGULAR'
    
    cam_obj = bpy.data.objects.new("VR_Camera_360", cam_data)
    cam_obj.location = (0, 0, 1.7)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-90)) # Olhando para o Norte
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    world = bpy.data.worlds.new("RealCosmicWorld")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.0003, 0.0006, 0.0015, 1.0)
    scene.world = world

    return scene

def build_planetarium_sky(scene, lat_deg, lst_hours, max_mag=6.0, R=80.0, show_constellation_lines=False, light_pollution_bortle=1):
    """
    Popula a cena do Blender com o céu real autêntico.
    Ajusta a magnitude limite de acordo com a escala de poluição luminosa (Bortle 1 a 9).
    """
    # Converter escala de Bortle (1-9) em magnitude limite de corte (mlim)
    # Bortle 1: mlim ~ 6.5
    # Bortle 4: mlim ~ 5.0
    # Bortle 7: mlim ~ 3.5
    # Bortle 9: mlim ~ 2.0
    bortle_to_mag = {
        1: 6.5, 2: 6.0, 3: 5.5, 4: 5.0, 5: 4.5,
        6: 4.0, 7: 3.5, 8: 2.8, 9: 2.0
    }
    effective_max_mag = min(max_mag, bortle_to_mag.get(light_pollution_bortle, 6.0))
    
    lat_rad = math.radians(lat_deg)
    lst_rad = math.radians(lst_hours * 15.0)
    
    stars = load_real_stars("data/hyg.csv", max_mag=effective_max_mag)
    print(f"[Planetarium Core] Carregando {len(stars)} estrelas reais (Bortle {light_pollution_bortle}, mag <= {effective_max_mag:.1f})...")

    # Emissões calibradas
    spectral_mats = {
        'O': create_emission_mat("StarMat_O", (0.75, 0.85, 1.0, 1.0), strength=14.0),
        'B': create_emission_mat("StarMat_B", (0.80, 0.90, 1.0, 1.0), strength=11.0),
        'A': create_emission_mat("StarMat_A", (0.95, 0.98, 1.0, 1.0), strength=8.5),
        'F': create_emission_mat("StarMat_F", (1.00, 1.00, 0.95, 1.0), strength=6.5),
        'G': create_emission_mat("StarMat_G", (1.00, 0.95, 0.70, 1.0), strength=5.5),
        'K': create_emission_mat("StarMat_K", (1.00, 0.75, 0.45, 1.0), strength=5.0),
        'M': create_emission_mat("StarMat_M", (1.00, 0.50, 0.30, 1.0), strength=5.0),
    }
    default_mat = create_emission_mat("StarMat_Def", (0.92, 0.95, 1.0, 1.0), strength=4.5)

    visible_count = 0
    for s in stars:
        alt_rad, az_rad = equatorial_to_horizontal(s['ra_rad'], s['dec_rad'], lat_rad, lst_rad)
        
        if alt_rad > math.radians(-0.5):
            visible_count += 1
            x = R * math.cos(alt_rad) * math.sin(az_rad)
            y = R * math.cos(alt_rad) * math.cos(az_rad)
            z = R * math.sin(alt_rad)
            
            mag = s['mag']
            # Escala de Pogson com contraste ampliado para estrelas brilhantes em poluição urbana
            radius = max(0.12, 0.65 * math.pow(10, -0.16 * mag))
            
            spect_char = s['spect'][0] if s['spect'] else 'A'
            mat = spectral_mats.get(spect_char, default_mat)
            
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=(x, y, z))
            star_obj = bpy.context.active_object
            star_obj.name = s['proper'] if s['proper'] else f"Star_{s['con']}_{mag:.1f}"
            star_obj.data.materials.append(mat)
            
    print(f"[Planetarium Core] Total de estrelas visíveis renderizadas: {visible_count}")
    return visible_count
