"""
Simulação IOAA - Problema 2: Determinar a Latitude do Observador (Desafio Secreto)
- Céu 100% autêntico do catálogo astronômico real HYG (Hipparcos/Yale)
- Latitude desafiada: -33.0° S
- Altitude do Polo Celeste Sul (SCP): 33.0° (Direção Sul)
- Tempo Sideral Local: LST ≈ 11h 32m (Mintaka se pondo exatamente no Oeste)
- 3 Estrelas mais brilhantes em suas posições reais no céu
- Cruzeiro do Sul (Crux) apontando para o SCP a 33° de altitude
- 3 Cometas com o Cometa 2 na Eclíptica (linha Regulus - Spica)
"""

import bpy
import math
import numpy as np
import os
import sys

sys.path.append(os.path.abspath("scripts"))
import build_real_sky_blender as sky_gen
import astro_engine

def build_southern_sky():
    scene = sky_gen.setup_clean_scene()
    
    # Nova Latitude Secreta de Desafio: -33.0° S
    lat_deg = -33.0
    lst_hours = 11.53
    R = 80.0
    sky_gen.populate_real_sky(scene, lat_deg=lat_deg, lst_hours=lst_hours, max_mag=6.0, R=R)
    
    comet_mat = sky_gen.create_emission_mat("CometMat", (1.0, 0.9, 0.15, 1.0), strength=12.0)
    tail_mat = sky_gen.create_emission_mat("TailMat", (1.0, 0.95, 0.3, 0.5), strength=3.0)
    ground_mat = sky_gen.create_emission_mat("GroundMat", (0.01, 0.015, 0.02, 1.0), strength=0.2)

    lat_rad = math.radians(lat_deg)
    lst_rad = math.radians(lst_hours * 15.0)

    # 1. Os 3 Cometas (Marcas Amarelas X com Cauda)
    # Cometa 2 na Eclíptica (entre Regulus e Spica)
    comets_equatorial = [
        ("Comet_1", math.radians(9.5 * 15.0), math.radians(-35.0)),
        ("Comet_2_Ecliptic", math.radians(11.8 * 15.0), math.radians(3.5)), # Na Eclíptica
        ("Comet_3", math.radians(15.2 * 15.0), math.radians(-48.0)),
    ]
    for name, ra_rad, dec_rad in comets_equatorial:
        alt_rad, az_rad = astro_engine.equatorial_to_horizontal(ra_rad, dec_rad, lat_rad, lst_rad)
        if alt_rad > 0.02:
            x = R * math.cos(alt_rad) * math.sin(az_rad)
            y = R * math.cos(alt_rad) * math.cos(az_rad)
            z = R * math.sin(alt_rad)
            
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.6, location=(x, y, z))
            c_obj = bpy.context.active_object
            c_obj.name = name
            c_obj.data.materials.append(comet_mat)
            
            bpy.ops.mesh.primitive_cone_add(radius1=0.7, depth=3.2, location=(x, y+0.4, z+0.4))
            tail = bpy.context.active_object
            tail.data.materials.append(tail_mat)

    # 2. Horizonte
    bpy.ops.mesh.primitive_cylinder_add(radius=85, depth=0.2, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.data.materials.append(ground_mat)

    os.makedirs("output_videos", exist_ok=True)
    scene.render.filepath = os.path.abspath("output_videos/raw_ioaa2019_p2_latitude25s.mp4")

if __name__ == "__main__":
    build_southern_sky()
