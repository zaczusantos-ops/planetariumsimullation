"""
Simulação IOAA 2019 - Problema 3: Observador na Lua em Mare Fecunditatis (0° N, 50° E)
- Evento: Eclipse Total do Sol pela Terra (Sol centralmente ocultado pela Terra)
- Posição no céu lunar: Altitude = 40° a Oeste (Azimute = 270°)
- Anel atmosférico avermelhado brilhante da Terra projetado no céu
- Planeta menor Juno (círculo amarelo) próximo ao eclipse a 3 UA do Sol (d_Lua ≈ 599 milhões de km)
- Solo lunar com relevo e crateras de Mare Fecunditatis
- Céu em Virgo / Outono na Hungria
"""

import bpy
import math
import numpy as np
import os

def setup_scene():
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
    scene.frame_end = 90

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

    world = bpy.data.worlds.new("LunarCosmicWorld")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.001, 0.002, 0.005, 1.0)
    scene.world = world

    return scene

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

def build_lunar_eclipse_scene():
    scene = setup_scene()
    
    star_mat = create_emission_mat("StarMat", (0.95, 0.98, 1.0, 1.0), strength=4.0)
    earth_disk_mat = create_emission_mat("EarthDiskMat", (0.02, 0.03, 0.08, 1.0), strength=0.5) # Disco escuro da Terra
    red_ring_mat = create_emission_mat("AtmosphereRingMat", (1.0, 0.25, 0.05, 1.0), strength=18.0) # Anel de fogo avermelhado do eclipse
    corona_mat = create_emission_mat("CoronaMat", (1.0, 0.95, 0.8, 1.0), strength=6.0) # Coroa solar externa
    juno_mat = create_emission_mat("JunoMat", (1.0, 0.85, 0.1, 1.0), strength=10.0) # Asteroide Juno amarelo
    lunar_regolith_mat = create_emission_mat("RegolithMat", (0.08, 0.08, 0.09, 1.0), strength=0.3)
    
    R = 80.0
    np.random.seed(999)
    
    # Campo estelar visto da Lua (sem atmosfera, estrelas super nítidas)
    for i in range(700):
        u = np.random.uniform(0, 1)
        v = np.random.uniform(0, 1)
        az = 2 * math.pi * u
        alt = math.asin(2 * v - 1)
        if alt > 0.02:
            x = R * math.cos(alt) * math.sin(az)
            y = R * math.cos(alt) * math.cos(az)
            z = R * math.sin(alt)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.18 + 0.12*np.random.rand(), location=(x, y, z))
            s = bpy.context.active_object
            s.data.materials.append(star_mat)

    # 1. Eclipse Total do Sol pela Terra: Altitude = 40° a Oeste (Az = 270°)
    # No sistema de coordenadas (x = Oeste = -cos(40°)*R, y = 0, z = sin(40°)*R)
    alt_ecl = math.radians(40)
    x_earth = -R * math.cos(alt_ecl)
    y_earth = 0
    z_earth = R * math.sin(alt_ecl)
    
    # Coroa Solar por trás da Terra
    bpy.ops.mesh.primitive_circle_add(radius=6.5, fill_type='NGON', location=(x_earth * 1.02, y_earth, z_earth * 1.02))
    corona = bpy.context.active_object
    corona.rotation_euler = (0, math.radians(-50), math.radians(90))
    corona.data.materials.append(corona_mat)

    # Disco da Terra (aproximadamente 2° de diâmetro aparente visto da Lua, 4x maior que o Sol)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=4.5, location=(x_earth, y_earth, z_earth))
    earth = bpy.context.active_object
    earth.name = "Earth_Eclipse_Disc"
    earth.data.materials.append(earth_disk_mat)

    # Anel atmosférico avermelhado brilhante (Refração da luz solar em volta da Terra)
    bpy.ops.mesh.primitive_torus_add(major_radius=4.6, minor_radius=0.25, location=(x_earth, y_earth, z_earth))
    red_ring = bpy.context.active_object
    red_ring.name = "Atmosphere_Red_Ring"
    red_ring.rotation_euler = (0, math.radians(-50), math.radians(90))
    red_ring.data.materials.append(red_ring_mat)

    # 2. Asteroide Juno (Círculo/ponto amarelo próximo ao eclipse)
    # Posição angular ligeiramente deslocada do Sol/Terra (Az ~ 265°, Alt ~ 43°)
    x_juno = -R * math.cos(math.radians(43)) * math.cos(math.radians(5))
    y_juno = -R * math.cos(math.radians(43)) * math.sin(math.radians(5))
    z_juno = R * math.sin(math.radians(43))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.7, location=(x_juno, y_juno, z_juno))
    juno = bpy.context.active_object
    juno.name = "Asteroid_Juno"
    juno.data.materials.append(juno_mat)

    # Indicador de anel amarelo ao redor de Juno
    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.08, location=(x_juno, y_juno, z_juno))
    juno_ring = bpy.context.active_object
    juno_ring.rotation_euler = (0, math.radians(-47), math.radians(90))
    juno_ring.data.materials.append(juno_mat)

    # 3. Solo Lunar de Mare Fecunditatis com crateras e pedras
    bpy.ops.mesh.primitive_cylinder_add(radius=85, depth=0.4, location=(0, 0, -0.2))
    ground = bpy.context.active_object
    ground.data.materials.append(lunar_regolith_mat)

    # Algumas rochas e elevações lunares no horizonte
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
