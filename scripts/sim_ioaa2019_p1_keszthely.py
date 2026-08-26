"""
Simulação IOAA 2019 - Problema 1: Céu Real de Keszthely (Hungria) à Meia-Noite
- Céu 100% fiel ao catálogo astronômico real HYG (Hipparcos/Yale)
- Latitude: +46.77° N
- Tempo Sideral Local (LST): 01h 00m (Gama Cassiopeiae culminando no meridiano superior)
- 3 Novas de 2ª magnitude destacadas em Pegasus, Cygnus e Auriga
- Aglomerados Globulares de Messier: M2, M13, M15, M30, M56, M71, M72, M92 em coordenadas reais
"""

import bpy
import math
import numpy as np
import os
import sys

sys.path.append(os.path.abspath("scripts"))
import planetarium_core as sky_gen

def build_keszthely_sky():
    scene = sky_gen.setup_vr_scene()
    
    # 1. Gerar o Céu Noturno Real com o Planetarium Core (sem linhas artificiais)
    lat_deg = 46.77
    lst_hours = 1.0  # 01h 00m
    R = 80.0
    sky_gen.build_planetarium_sky(scene, lat_deg=lat_deg, lst_hours=lst_hours, max_mag=6.0, R=R, show_constellation_lines=False)
    
    # Materiais especiais
    nova_mat = sky_gen.create_emission_mat("NovaMat", (1.0, 0.25, 0.1, 1.0), strength=15.0)
    cluster_mat = sky_gen.create_emission_mat("ClusterMat", (0.2, 0.85, 1.0, 1.0), strength=8.0)
    grid_mat = sky_gen.create_emission_mat("GridMat", (0.0, 0.6, 0.8, 1.0), strength=2.0)
    ground_mat = sky_gen.create_emission_mat("GroundMat", (0.01, 0.02, 0.03, 1.0), strength=0.2)

    lat_rad = math.radians(lat_deg)
    lst_rad = math.radians(lst_hours * 15.0)

    # 2. As 3 Novas de 2ª magnitude da prova em posições específicas
    # (Pegasus, Cygnus, Auriga)
    novae_equatorial = [
        ("Nova_Pegasus", math.radians(23.2 * 15.0), math.radians(25.0)), # Em Pegasus
        ("Nova_Cygnus", math.radians(20.5 * 15.0), math.radians(42.0)),  # Em Cygnus
        ("Nova_Auriga", math.radians(5.5 * 15.0), math.radians(38.0)),   # Em Auriga
    ]
    for name, ra_rad, dec_rad in novae_equatorial:
        alt_rad, az_rad = astro_engine.equatorial_to_horizontal(ra_rad, dec_rad, lat_rad, lst_rad)
        if alt_rad > 0:
            x = R * math.cos(alt_rad) * math.sin(az_rad)
            y = R * math.cos(alt_rad) * math.cos(az_rad)
            z = R * math.sin(alt_rad)
            
            # Ponto brilhante da Nova
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.75, location=(x, y, z))
            nova = bpy.context.active_object
            nova.name = name
            nova.data.materials.append(nova_mat)
            
            # Anel indicador da prova
            bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.08, location=(x, y, z))
            ring = bpy.context.active_object
            ring.data.materials.append(nova_mat)

    # 3. Aglomerados Globulares de Messier com coordenadas equatoriais reais (RA, Dec)
    # M2, M13, M15, M30, M56, M71, M72, M92
    messier_clusters = [
        ("M13_Hercules", math.radians((16 + 41.7/60)*15), math.radians(36 + 27/60)),
        ("M92_Hercules", math.radians((17 + 17.1/60)*15), math.radians(43 + 8/60)),
        ("M15_Pegasus", math.radians((21 + 29.9/60)*15), math.radians(12 + 10/60)),
        ("M2_Aquarius", math.radians((21 + 33.5/60)*15), math.radians(-0 - 49/60)),
        ("M56_Lyra", math.radians((19 + 16.6/60)*15), math.radians(30 + 11/60)),
        ("M71_Sagitta", math.radians((19 + 53.8/60)*15), math.radians(18 + 47/60)),
        ("M30_Capricornus", math.radians((21 + 40.4/60)*15), math.radians(-23 - 11/60)),
        ("M72_Aquarius", math.radians((20 + 53.5/60)*15), math.radians(-12 - 32/60)),
    ]
    for name, ra_rad, dec_rad in messier_clusters:
        alt_rad, az_rad = astro_engine.equatorial_to_horizontal(ra_rad, dec_rad, lat_rad, lst_rad)
        if alt_rad > 0.05:
            x = R * math.cos(alt_rad) * math.sin(az_rad)
            y = R * math.cos(alt_rad) * math.cos(az_rad)
            z = R * math.sin(alt_rad)
            
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.45, location=(x, y, z))
            cl = bpy.context.active_object
            cl.name = name
            cl.data.materials.append(cluster_mat)

    # 4. Linha Meridiana Real (Norte - Zênite - Sul)
    curve_data = bpy.data.curves.new('MeridianLine', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(30)
    for idx, angle_deg in enumerate(np.linspace(0, 180, 31)):
        ang = math.radians(angle_deg)
        y = R * math.cos(ang)
        z = R * math.sin(ang)
        polyline.points[idx].co = (0, y, z, 1)
        
    curve_obj = bpy.data.objects.new('MeridianLineObj', curve_data)
    curve_data.bevel_depth = 0.12
    curve_obj.data.materials.append(grid_mat)
    scene.collection.objects.link(curve_obj)

    # 5. Horizonte Terrestre de Keszthely
    bpy.ops.mesh.primitive_cylinder_add(radius=85, depth=0.2, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.data.materials.append(ground_mat)

    os.makedirs("output_videos", exist_ok=True)
    scene.render.filepath = os.path.abspath("output_videos/raw_ioaa2019_p1_keszthely.mp4")

if __name__ == "__main__":
    build_keszthely_sky()
