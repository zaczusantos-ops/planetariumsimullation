"""
Simulação IOAA 2019 - Problema 2: Observador a 25° de Latitude Sul
- Altitude do Polo Celeste Sul (SCP): 25° (Direção Sul)
- Cruzeiro do Sul (Crux) apontando para o SCP a 25°
- 3 Estrelas mais brilhantes com seus azimutes exatos:
  1. Sirius (alfa CMa, mV = -1.46) em Az = 82° (Leste)
  2. Canopus (alfa Car, mV = -0.74) em Az = 42° (Nordeste)
  3. Toliman / Alpha Centauri (alfa Cen, mV = -0.27) em Az = 331° (Noroeste)
- 3 Cometas (marcas amarelas X), com o Cometa 2 na Eclíptica
- Mintaka (delta Orionis) se pondo exatamente no horizonte Oeste (Az = 270°, Alt = 0°)
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

    world = bpy.data.worlds.new("CosmicWorld")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.002, 0.003, 0.008, 1.0)
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

def build_southern_sky():
    scene = setup_scene()
    
    star_mat = create_emission_mat("StarMat", (0.9, 0.95, 1.0, 1.0), strength=4.0)
    sirius_mat = create_emission_mat("SiriusMat", (0.8, 0.9, 1.0, 1.0), strength=15.0) # Brilho intenso azul-branco
    canopus_mat = create_emission_mat("CanopusMat", (1.0, 0.98, 0.9, 1.0), strength=12.0)
    toliman_mat = create_emission_mat("TolimanMat", (1.0, 0.85, 0.5, 1.0), strength=10.0)
    comet_mat = create_emission_mat("CometMat", (1.0, 0.9, 0.1, 1.0), strength=8.0) # Amarelo cometa
    ecliptic_mat = create_emission_mat("EclipticMat", (0.2, 0.8, 0.3, 1.0), strength=2.0) # Verde suave
    
    R = 80.0
    np.random.seed(123)
    
    # Campo de estrelas do hemisfério sul
    for i in range(500):
        u = np.random.uniform(0, 1)
        v = np.random.uniform(0, 1)
        az = 2 * math.pi * u
        alt = math.asin(2 * v - 1)
        if alt > 0.04:
            x = R * math.cos(alt) * math.sin(az)
            y = R * math.cos(alt) * math.cos(az)
            z = R * math.sin(alt)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15 + 0.1*np.random.rand(), location=(x, y, z))
            s = bpy.context.active_object
            s.data.materials.append(star_mat)

    # 1. As 3 Estrelas Mais Brilhantes nos Azimutes do Gabarito
    bright_stars = [
        ("Sirius", math.radians(82), math.radians(38), sirius_mat, 1.2),
        ("Canopus", math.radians(42), math.radians(52), canopus_mat, 1.0),
        ("Toliman_AlphaCen", math.radians(331), math.radians(45), toliman_mat, 0.9),
    ]
    for name, az, alt, mat, r_size in bright_stars:
        x = R * math.cos(alt) * math.sin(az)
        y = R * math.cos(alt) * math.cos(az)
        z = R * math.sin(alt)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r_size, location=(x, y, z))
        star_obj = bpy.context.active_object
        star_obj.name = name
        star_obj.data.materials.append(mat)

    # 2. Cruzeiro do Sul (Crux) e Polo Celeste Sul a 25° de altitude no Sul (Az = 180°)
    # Polo Celeste Sul: Az = 180°, Alt = 25°
    x_scp = 0
    y_scp = -R * math.cos(math.radians(25))
    z_scp = R * math.sin(math.radians(25))
    
    # Anel marcador do Polo Celeste Sul
    bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.08, location=(x_scp, y_scp, z_scp))
    scp_ring = bpy.context.active_object
    scp_ring.rotation_euler = (math.radians(-65), 0, 0)
    scp_ring.data.materials.append(create_emission_mat("SCPMat", (0.0, 0.8, 1.0, 1.0), strength=4.0))

    # 3. Mintaka (delta Orionis) se pondo exatamente no horizonte Oeste (Az = 270°, Alt = 0.5°)
    x_mintaka = -R * math.cos(math.radians(0.5))
    y_mintaka = 0
    z_mintaka = R * math.sin(math.radians(0.5))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.6, location=(x_mintaka, y_mintaka, z_mintaka))
    mintaka = bpy.context.active_object
    mintaka.name = "Mintaka_Setting"
    mintaka.data.materials.append(create_emission_mat("MintakaMat", (1.0, 0.6, 0.2, 1.0), strength=8.0))

    # 4. Os 3 Cometas (Amarelos com formato de cauda suave)
    # Cometa 2 exatamente sobre a Eclíptica
    comets = [
        ("Comet_1", math.radians(120), math.radians(30)),
        ("Comet_2_Ecliptic", math.radians(210), math.radians(45)), # Na Eclíptica
        ("Comet_3", math.radians(300), math.radians(20)),
    ]
    for name, az, alt in comets:
        x = R * math.cos(alt) * math.sin(az)
        y = R * math.cos(alt) * math.cos(az)
        z = R * math.sin(alt)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.6, location=(x, y, z))
        c_obj = bpy.context.active_object
        c_obj.name = name
        c_obj.data.materials.append(comet_mat)
        
        # Cauda do cometa
        bpy.ops.mesh.primitive_cone_add(radius1=0.8, depth=3.5, location=(x, y+0.5, z+0.5))
        tail = bpy.context.active_object
        tail.data.materials.append(create_emission_mat("TailMat", (1.0, 0.9, 0.2, 0.4), strength=3.0))

    # 5. Horizonte e Solo
    bpy.ops.mesh.primitive_cylinder_add(radius=85, depth=0.2, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.data.materials.append(create_emission_mat("GroundMat", (0.01, 0.015, 0.02, 1.0), strength=0.2))

    os.makedirs("output_videos", exist_ok=True)
    scene.render.filepath = os.path.abspath("output_videos/raw_ioaa2019_p2_latitude25s.mp4")

if __name__ == "__main__":
    build_southern_sky()
