"""
Simulação Planetário IOAA: 'Quando o segundo Sol chegar...'
Sistema Binário Plo-I e Plo-II com observador no planeta em rotação síncrona.
Câmera 360° Equirectangular VR no horizonte do planeta.
"""

import bpy
import math
import os
import numpy as np

def create_vr_planetarium_scene():
    # 1. Resetar cena
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 2. Configurações de Render
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 2  # Cenas espaciais e emissivas ficam limpas com poucos samples
    scene.cycles.max_bounces = 1
    scene.cycles.diffuse_bounces = 0
    scene.cycles.glossy_bounces = 0
    scene.cycles.transmission_bounces = 0
    scene.cycles.transparent_max_bounces = 1
    scene.cycles.use_denoising = False
    
    # Resolução 2:1 Equiretangular para VR
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 960
    scene.render.fps = 30
    total_frames = 120  # 4 segundos (2 ciclos completos do binário)
    scene.frame_start = 1
    scene.frame_end = total_frames
    
    # 3. Configurar World Shader (Céu estrelado de fundo)
    world = bpy.data.worlds.new("CosmicWorld")
    scene.world = world
    world.use_nodes = True
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links
    w_nodes.clear()
    
    node_w_out = w_nodes.new(type='ShaderNodeOutputWorld')
    node_bg = w_nodes.new(type='ShaderNodeBackground')
    node_bg.inputs['Color'].default_value = (0.01, 0.01, 0.025, 1.0)  # Azul cósmico escuro
    node_bg.inputs['Strength'].default_value = 1.0
    w_links.new(node_bg.outputs['Background'], node_w_out.inputs['Surface'])
    
    # 4. Criar Câmera Panorâmica 360 VR (Observador no planeta)
    cam_data = bpy.data.cameras.new("VR_Camera_360")
    cam_data.type = 'PANO'
    if hasattr(cam_data, 'panorama_type'):
        cam_data.panorama_type = 'EQUIRECTANGULAR'
    elif hasattr(cam_data, 'cycles'):
        cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'
    cam_obj = bpy.data.objects.new("VR_Camera_360", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, 0, 1.7)  # Altura dos olhos do observador (1.7m)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(0))  # Olhando para o horizonte
    
    # 5. Criar Terreno / Piso do Observador com Rosa dos Ventos
    bpy.ops.mesh.primitive_cylinder_add(radius=150, depth=0.2, location=(0, 0, -0.1))
    ground = bpy.context.active_object
    ground.name = "Ground_Planet"
    
    mat_ground = bpy.data.materials.new(name="GroundMat")
    mat_ground.use_nodes = True
    g_nodes = mat_ground.node_tree.nodes
    g_bsdf = g_nodes.get('Principled BSDF')
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.05, 0.07, 0.08, 1.0)
        g_bsdf.inputs['Roughness'].default_value = 0.9
    ground.data.materials.append(mat_ground)
    
    # 6. Criar Domo de Estrelas Fixas (Esfera externa rotacionando para simular céu noturno / translação)
    # Na questão: o planeta é síncrono com o CM (T_rot = T_trans), então as estrelas fixas giram no céu!
    bpy.ops.mesh.primitive_uv_sphere_add(radius=300, location=(0, 0, 0))
    star_dome = bpy.context.active_object
    star_dome.name = "StarDome_FixedStars"
    
    # Material com textura procedural de estrelas (Voronoi + ColorRamp)
    mat_stars = bpy.data.materials.new(name="StarsMat")
    mat_stars.use_nodes = True
    s_nodes = mat_stars.node_tree.nodes
    s_links = mat_stars.node_tree.links
    s_nodes.clear()
    
    s_out = s_nodes.new(type='ShaderNodeOutputMaterial')
    s_emit = s_nodes.new(type='ShaderNodeEmission')
    s_ramp = s_nodes.new(type='ShaderNodeValToRGB')
    s_ramp.color_ramp.elements[0].position = 0.985
    s_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    s_ramp.color_ramp.elements[1].position = 0.998
    s_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    
    s_tex = s_nodes.new(type='ShaderNodeTexVoronoi')
    s_tex.inputs['Scale'].default_value = 120.0
    
    s_links.new(s_tex.outputs['Distance'], s_ramp.inputs['Fac'])
    s_links.new(s_ramp.outputs['Color'], s_emit.inputs['Color'])
    s_emit.inputs['Strength'].default_value = 8.0
    s_links.new(s_emit.outputs['Emission'], s_out.inputs['Surface'])
    
    star_dome.data.materials.append(mat_stars)
    # Inverter normais para ficar visível de dentro
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Animar rotação do domo de estrelas de fundo (1 rotação durante o período de translação)
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        angle = 2 * math.pi * (f / total_frames)
        star_dome.rotation_euler = (0, 0, angle)
        star_dome.keyframe_insert(data_path="rotation_euler", frame=f)
        
    # 7. Criar Linha do Meridiano Local no Céu (Arco de referência visual)
    # Na questão: as estrelas e o CM estão SEMPRE sobre o meridiano local!
    curve_data = bpy.data.curves.new('MeridianLine', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    
    num_pts = 64
    polyline.points.add(num_pts - 1)
    r_meridian = 180.0
    for i in range(num_pts):
        th = math.pi * (i / (num_pts - 1))  # de 0 (Horizonte Sul) a pi (Horizonte Norte)
        x = 0
        y = r_meridian * math.cos(th)
        z = r_meridian * math.sin(th)
        polyline.points[i].co = (x, y, z, 1)
        
    curve_data.bevel_depth = 0.4
    meridian_obj = bpy.data.objects.new('Meridian_Line', curve_data)
    scene.collection.objects.link(meridian_obj)
    
    mat_meridian = bpy.data.materials.new(name="MeridianMat")
    mat_meridian.use_nodes = True
    m_emit = mat_meridian.node_tree.nodes.get('Principled BSDF')
    if m_emit:
        m_emit.inputs['Base Color'].default_value = (0.2, 0.8, 1.0, 1.0)
        m_emit.inputs['Emission Color'].default_value = (0.1, 0.5, 1.0, 1.0)
        m_emit.inputs['Emission Strength'].default_value = 2.0
    meridian_obj.data.materials.append(mat_meridian)
    
    # 8. Centro de Massa (CM) - Marcador fixo a altura h = 45° no meridiano local
    alt_cm = math.radians(45)  # Altura fixa do CM
    r_sky = 200.0
    cm_y = r_sky * math.cos(alt_cm)
    cm_z = r_sky * math.sin(alt_cm)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, cm_y, cm_z))
    cm_marker = bpy.context.active_object
    cm_marker.name = "Centro_de_Massa"
    
    mat_cm = bpy.data.materials.new(name="CMMat")
    mat_cm.use_nodes = True
    cm_nodes = mat_cm.node_tree.nodes
    cm_nodes.clear()
    cm_emit = cm_nodes.new(type='ShaderNodeEmission')
    cm_emit.inputs['Color'].default_value = (0.0, 1.0, 0.4, 1.0)  # Verde fluorescente
    cm_emit.inputs['Strength'].default_value = 5.0
    cm_out = cm_nodes.new(type='ShaderNodeOutputMaterial')
    mat_cm.node_tree.links.new(cm_emit.outputs['Emission'], cm_out.inputs['Surface'])
    cm_marker.data.materials.append(mat_cm)
    
    # 9. Estrelas do Binário: Plo-I (Maior massa m1) e Plo-II (Menor massa m2)
    # Razão de massa: m1 = 2 * m2  =>  r1 = 1/3 d,  r2 = 2/3 d
    # As estrelas orbitam o CM no plano do meridiano local (coplanares com o observador)
    d_ang = math.radians(18)  # Separação angular máxima no céu
    r_orbit_I = (1.0 / 3.0) * d_ang
    r_orbit_II = (2.0 / 3.0) * d_ang
    
    # Estrela Plo-I (Amarela, mais massiva)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=4.5, location=(0, cm_y, cm_z))
    plo1 = bpy.context.active_object
    plo1.name = "Plo-I"
    
    mat_plo1 = bpy.data.materials.new(name="Plo1Mat")
    mat_plo1.use_nodes = True
    p1_nodes = mat_plo1.node_tree.nodes
    p1_nodes.clear()
    p1_emit = p1_nodes.new(type='ShaderNodeEmission')
    p1_emit.inputs['Color'].default_value = (1.0, 0.9, 0.5, 1.0)  # Amarelo solar
    p1_emit.inputs['Strength'].default_value = 25.0
    p1_out = p1_nodes.new(type='ShaderNodeOutputMaterial')
    mat_plo1.node_tree.links.new(p1_emit.outputs['Emission'], p1_out.inputs['Surface'])
    plo1.data.materials.append(mat_plo1)
    
    # Luz da Plo-I
    light_p1 = bpy.data.lights.new(name="Plo1_Light", type='POINT')
    light_p1.energy = 50000.0
    light_p1.color = (1.0, 0.9, 0.5)
    light_p1_obj = bpy.data.objects.new("Plo1_Light", light_p1)
    scene.collection.objects.link(light_p1_obj)
    
    # Estrela Plo-II (Alaranjada/Vermelha, menos massiva, órbita mais ampla)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.8, location=(0, cm_y, cm_z))
    plo2 = bpy.context.active_object
    plo2.name = "Plo-II"
    
    mat_plo2 = bpy.data.materials.new(name="Plo2Mat")
    mat_plo2.use_nodes = True
    p2_nodes = mat_plo2.node_tree.nodes
    p2_nodes.clear()
    p2_emit = p2_nodes.new(type='ShaderNodeEmission')
    p2_emit.inputs['Color'].default_value = (1.0, 0.35, 0.1, 1.0)  # Laranja/Vermelho
    p2_emit.inputs['Strength'].default_value = 15.0
    p2_out = p2_nodes.new(type='ShaderNodeOutputMaterial')
    mat_plo2.node_tree.links.new(p2_emit.outputs['Emission'], p2_out.inputs['Surface'])
    plo2.data.materials.append(mat_plo2)
    
    # Luz da Plo-II
    light_p2 = bpy.data.lights.new(name="Plo2_Light", type='POINT')
    light_p2.energy = 20000.0
    light_p2.color = (1.0, 0.4, 0.1)
    light_p2_obj = bpy.data.objects.new("Plo2_Light", light_p2)
    scene.collection.objects.link(light_p2_obj)
    
    # 10. Animar Órbita do Binário (Plo-I e Plo-II oscilando ao longo do meridiano local)
    # Período binário = 60 frames (4 rotações completas ao longo da simulação de 240 frames)
    binary_period_frames = 60
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        phase = 2 * math.pi * (f / binary_period_frames)
        
        # Ângulos ao longo do meridiano local
        # Plo-I oscila com amplitude r_orbit_I
        theta_1 = alt_cm + r_orbit_I * math.sin(phase)
        y1 = r_sky * math.cos(theta_1)
        z1 = r_sky * math.sin(theta_1)
        plo1.location = (0, y1, z1)
        light_p1_obj.location = (0, y1, z1)
        plo1.keyframe_insert(data_path="location", frame=f)
        light_p1_obj.keyframe_insert(data_path="location", frame=f)
        
        # Plo-II oscila em oposição de fase (phase + pi) com amplitude maior r_orbit_II
        theta_2 = alt_cm - r_orbit_II * math.sin(phase)
        y2 = r_sky * math.cos(theta_2)
        z2 = r_sky * math.sin(theta_2)
        plo2.location = (0, y2, z2)
        light_p2_obj.location = (0, y2, z2)
        plo2.keyframe_insert(data_path="location", frame=f)
        light_p2_obj.keyframe_insert(data_path="location", frame=f)

    # 11. Configurações de Exportação de Vídeo
    os.makedirs("output_videos", exist_ok=True)
    raw_video_path = os.path.abspath("output_videos/raw_quando_o_segundo_sol_chegar.mp4")
    if hasattr(scene.render.image_settings, 'media_type'):
        scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = raw_video_path
    
    print(f"Iniciando renderização de {total_frames} frames em 360° VR...")
    bpy.ops.render.render(animation=True)
    print(f"Renderização concluída! Salvo em: {raw_video_path}")

if __name__ == "__main__":
    create_vr_planetarium_scene()
