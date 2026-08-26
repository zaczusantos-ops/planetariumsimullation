"""
Simulação IOAA 2019 - Problema 3: Observador na Lua em Mare Fecunditatis (0° N, 50° E)
- Céu 100% autêntico do catálogo astronômico real HYG na direção de Virgo / Equinócio de Outono
- Eclipse Total do Sol pela Terra a 40° de altitude a Oeste (Azimute = 270°)
- Anel atmosférico avermelhado refratado pela Terra e coroa solar
- Planeta menor Juno próximo ao Sol a 3 UA de distância
- Relevo e rochas da superfície lunar de Mare Fecunditatis
"""

import bpy
import math
import numpy as np
import os
import sys

sys.path.append(os.path.abspath("scripts"))
import planetarium_core as sky_gen

def build_lunar_eclipse_scene():
    scene = sky_gen.setup_vr_scene()
    
    # Campo estelar visto da Lua (Equinócio de Outono: Sol em Virgo, RA ~ 12h, Dec ~ 0°)
    lst_hours = 14.67
    lat_deg = 0.0 # Equador lunar
    R = 80.0
    sky_gen.build_planetarium_sky(scene, lat_deg=lat_deg, lst_hours=lst_hours, max_mag=6.0, R=R, show_constellation_lines=False)

    earth_disk_mat = sky_gen.create_emission_mat("EarthDiskMat", (0.015, 0.025, 0.06, 1.0), strength=0.5)
    red_ring_mat = sky_gen.create_emission_mat("AtmosphereRingMat", (1.0, 0.22, 0.05, 1.0), strength=20.0)
    corona_mat = sky_gen.create_emission_mat("CoronaMat", (1.0, 0.95, 0.8, 1.0), strength=6.0)
    juno_mat = sky_gen.create_emission_mat("JunoMat", (1.0, 0.88, 0.1, 1.0), strength=12.0)
    lunar_regolith_mat = sky_gen.create_emission_mat("RegolithMat", (0.07, 0.07, 0.08, 1.0), strength=0.3)

    # 1. Eclipse Total do Sol pela Terra: Altitude = 40° a Oeste (Az = 270°)
    alt_ecl = math.radians(40)
    x_earth = -R * math.cos(alt_ecl)
    y_earth = 0
    z_earth = R * math.sin(alt_ecl)
    
    # Coroa Solar por trás da Terra
    bpy.ops.mesh.primitive_circle_add(radius=6.5, fill_type='NGON', location=(x_earth * 1.02, y_earth, z_earth * 1.02))
    corona = bpy.context.active_object
    corona.rotation_euler = (0, math.radians(-50), math.radians(90))
    corona.data.materials.append(corona_mat)

    # Disco da Terra
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=4.5, location=(x_earth, y_earth, z_earth))
    earth = bpy.context.active_object
    earth.name = "Earth_Eclipse_Disc"
    earth.data.materials.append(earth_disk_mat)

    # Anel atmosférico avermelhado brilhante (Refração da luz solar ao redor da atmosfera terrestre)
    bpy.ops.mesh.primitive_torus_add(major_radius=4.6, minor_radius=0.25, location=(x_earth, y_earth, z_earth))
    red_ring = bpy.context.active_object
    red_ring.name = "Atmosphere_Red_Ring"
    red_ring.rotation_euler = (0, math.radians(-50), math.radians(90))
    red_ring.data.materials.append(red_ring_mat)

    # 2. Asteroide Juno (ponto amarelo próximo ao Sol a 3 UA do Sol)
    x_juno = -R * math.cos(math.radians(43)) * math.cos(math.radians(5))
    y_juno = -R * math.cos(math.radians(43)) * math.sin(math.radians(5))
    z_juno = R * math.sin(math.radians(43))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.7, location=(x_juno, y_juno, z_juno))
    juno = bpy.context.active_object
    juno.name = "Asteroid_Juno"
    juno.data.materials.append(juno_mat)

    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.08, location=(x_juno, y_juno, z_juno))
    juno_ring = bpy.context.active_object
    juno_ring.rotation_euler = (0, math.radians(-47), math.radians(90))
    juno_ring.data.materials.append(juno_mat)

    # 3. Solo Lunar de Mare Fecunditatis
    bpy.ops.mesh.primitive_cylinder_add(radius=85, depth=0.4, location=(0, 0, -0.2))
    ground = bpy.context.active_object
    ground.data.materials.append(lunar_regolith_mat)

    np.random.seed(777)
    for i in range(18):
        ang = np.random.uniform(0, 2*np.pi)
        dist = np.random.uniform(15, 60)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=np.random.uniform(0.5, 2.5), location=(dist*math.cos(ang), dist*math.sin(ang), 0.2))
        rock = bpy.context.active_object
        rock.data.materials.append(lunar_regolith_mat)

    os.makedirs("output_videos", exist_ok=True)
    scene.render.filepath = os.path.abspath("output_videos/raw_ioaa2019_p3_lunar_eclipse.mp4")

if __name__ == "__main__":
    build_lunar_eclipse_scene()
