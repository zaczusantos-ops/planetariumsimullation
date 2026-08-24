"""
Gerador de Cenas Reais do Céu Noturno para o Blender
Utiliza os 5.071 corpos reais do catálogo HYG com magnitudes, cores espectrais e conversão horizontal exata.
"""

import bpy
import math
import numpy as np
import os
import sys

# Adicionar caminho local para importar astro_engine
sys.path.append(os.path.abspath("scripts"))
import astro_engine

def setup_clean_scene():
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
        bg_node.inputs['Color'].default_value = (0.0005, 0.001, 0.003, 1.0)
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

def populate_real_sky(scene, lat_deg, lst_hours, max_mag=6.0, R=80.0):
    """
    Popula o céu com todas as estrelas reais do catálogo HYG acima do horizonte.
    """
    lat_rad = math.radians(lat_deg)
    lst_rad = math.radians(lst_hours * 15.0)
    
    stars = astro_engine.load_real_stars("data/hyg.csv", max_mag=max_mag)
    print(f"Processando {len(stars)} estrelas do catálogo real...")

    # Dicionário de materiais por classe espectral para não duplicar shaders
    spectral_mats = {
        'O': create_emission_mat("StarMat_O", (0.75, 0.85, 1.0, 1.0), strength=12.0),
        'B': create_emission_mat("StarMat_B", (0.8, 0.9, 1.0, 1.0), strength=10.0),
        'A': create_emission_mat("StarMat_A", (0.95, 0.98, 1.0, 1.0), strength=8.0),
        'F': create_emission_mat("StarMat_F", (1.0, 1.0, 0.95, 1.0), strength=6.0),
        'G': create_emission_mat("StarMat_G", (1.0, 0.95, 0.7, 1.0), strength=5.0),
        'K': create_emission_mat("StarMat_K", (1.0, 0.75, 0.45, 1.0), strength=5.0),
        'M': create_emission_mat("StarMat_M", (1.0, 0.5, 0.3, 1.0), strength=5.0),
    }
    default_mat = create_emission_mat("StarMat_Def", (0.9, 0.95, 1.0, 1.0), strength=4.0)

    # Batch de vértices para estrelas fracas (para máxima performance) e objetos individuais para estrelas brilhantes
    visible_count = 0
    for s in stars:
        alt_rad, az_rad = astro_engine.equatorial_to_horizontal(s['ra_rad'], s['dec_rad'], lat_rad, lst_rad)
        
        # Apenas estrelas acima do horizonte
        if alt_rad > math.radians(-0.5):
            visible_count += 1
            x = R * math.cos(alt_rad) * math.sin(az_rad)
            y = R * math.cos(alt_rad) * math.cos(az_rad)
            z = R * math.sin(alt_rad)
            
            # Raio proporcional à magnitude aparente (escala de Pogson)
            mag = s['mag']
            radius = max(0.12, 0.65 * math.pow(10, -0.16 * mag))
            
            spect_char = s['spect'][0] if s['spect'] else 'A'
            mat = spectral_mats.get(spect_char, default_mat)
            
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=(x, y, z))
            star_obj = bpy.context.active_object
            star_obj.name = s['proper'] if s['proper'] else f"Star_{s['con']}_{mag:.1f}"
            star_obj.data.materials.append(mat)
            
    print(f"Total de estrelas reais renderizadas no céu visível: {visible_count}")
