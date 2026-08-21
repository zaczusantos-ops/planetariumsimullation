"""
Template de simulação orbital e renderização VR 360° no Blender.
Execução: blender -b -P scripts/sample_orbit_sim.py
"""

import sys
import math
import os

try:
    import bpy
    import numpy as np
except ImportError:
    print("Este script deve ser executado pelo interpretador Python embutido no Blender.")
    print("Comando: blender -b -P scripts/sample_orbit_sim.py")
    sys.exit(0)

def build_vr_planetarium():
    # 1. Resetar cena
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 2. Configurações de Render
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU' if bpy.context.preferences.addons.get('cycles') else 'CPU'
    scene.render.resolution_x = 1920  # Preview (3840 para 4K)
    scene.render.resolution_y = 960   # Preview (1920 para 4K)
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 150  # 5 segundos
    
    # 3. Câmera Panorâmica 360 VR (Observador)
    cam_data = bpy.data.cameras.new("VR_Observador")
    cam_data.type = 'PANO'
    if hasattr(cam_data, 'panorama_type'):
        cam_data.panorama_type = 'EQUIRECTANGULAR'
    elif hasattr(cam_data, 'cycles'):
        cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'
    cam_obj = bpy.data.objects.new("VR_Observador", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, 0, 0)
    
    # 4. Sol (Estrela Central)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 0))
    sun = bpy.context.active_object
    sun.name = "Sol"
    
    # Material emissivo para o Sol
    mat_sun = bpy.data.materials.new(name="SunMat")
    nodes = mat_sun.node_tree.nodes
    nodes.clear()
    node_emit = nodes.new(type='ShaderNodeEmission')
    node_emit.inputs['Color'].default_value = (1.0, 0.85, 0.4, 1.0)
    node_emit.inputs['Strength'].default_value = 15.0
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    mat_sun.node_tree.links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    sun.data.materials.append(mat_sun)
    
    # 5. Planeta
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(8, 0, 0))
    planet = bpy.context.active_object
    planet.name = "Planeta"
    
    # 6. Animação Orbital Kepleriana
    a = 8.0  # Semi-eixo maior
    e = 0.5  # Excentricidade
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        M = 2 * math.pi * (f / scene.frame_end)
        E = M
        for _ in range(5):  # Método de Newton-Raphson para equação de Kepler
            E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        
        x = a * (math.cos(E) - e)
        y = a * math.sqrt(1 - e**2) * math.sin(E)
        planet.location = (x, y, 0)
        planet.keyframe_insert(data_path="location", frame=f)

    # 7. Configuração de Saída de Vídeo
    os.makedirs("output_videos", exist_ok=True)
    if hasattr(scene.render.image_settings, 'media_type'):
        scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath = os.path.abspath("output_videos/raw_simulacao.mp4")
    
    print("Iniciando renderização da simulação VR...")
    bpy.ops.render.render(animation=True)
    print("Renderização concluída!")

if __name__ == "__main__":
    build_vr_planetarium()
