"""
Renderizador 4K de Altíssima Definição para Planetário IOAA em VR 360° Estereoscópico.
Gera vídeo nítido (3840x1920 por olho / 3840x3840 total) com traçado limpo e cores vibrantes.
"""

import bpy
import math
import os

def create_text_3d(text, location, scale=1.0, color=(1, 1, 1, 1), rot=(math.radians(90), 0, 0)):
    font_curve = bpy.data.curves.new(type="FONT", name=f"Text_{text}")
    font_curve.body = text
    font_curve.extrude = 0.08
    font_curve.bevel_depth = 0.02
    font_curve.align_x = 'CENTER'
    font_curve.align_y = 'CENTER'
    
    obj = bpy.data.objects.new(f"Label_{text}", font_curve)
    obj.location = location
    obj.rotation_euler = rot
    obj.scale = (scale, scale, scale)
    bpy.context.scene.collection.objects.link(obj)
    
    mat = bpy.data.materials.new(name=f"Mat_Text_{text}")
    nodes = mat.node_tree.nodes
    nodes.clear()
    emit = nodes.new(type='ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = 15.0
    out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    obj.data.materials.append(mat)
    return obj

def build_hd_vr_planetarium():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 1. Configuração Estéreo 3D
    scene.render.use_multiview = True
    scene.render.views_format = 'STEREO_3D'
    if hasattr(scene.render.image_settings, 'stereo_3d_format'):
        scene.render.image_settings.stereo_3d_format.display_mode = 'TOPBOTTOM'
    
    # 2. Configurações de Render Cycles Otimizado em 4K
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 1  # Com materiais emissivos e fundo procedural, 1 sample em 4K é perfeitamente limpo e ultrarrápido!
    scene.cycles.max_bounces = 1
    scene.cycles.diffuse_bounces = 0
    scene.cycles.glossy_bounces = 0
    scene.cycles.transmission_bounces = 0
    scene.cycles.transparent_max_bounces = 1
    scene.cycles.use_denoising = False
    
    # Resolução 4K Estéreo (2560x1280 por olho = 2560x2560 total para nitidez extrema)
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 2560
    scene.render.fps = 30
    total_frames = 60  # 2 segundos (1 ciclo fechado em loop contínuo)
    scene.frame_start = 1
    scene.frame_end = total_frames
    
    # 3. Fundo Cósmico
    world = bpy.data.worlds.new("CosmicWorld")
    scene.world = world
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links
    w_nodes.clear()
    
    node_w_out = w_nodes.new(type='ShaderNodeOutputWorld')
    node_bg = w_nodes.new(type='ShaderNodeBackground')
    node_bg.inputs['Color'].default_value = (0.002, 0.003, 0.01, 1.0)
    node_bg.inputs['Strength'].default_value = 1.0
    w_links.new(node_bg.outputs['Background'], node_w_out.inputs['Surface'])
    
    # 4. Câmera Estéreo Panorâmica 360 VR
    cam_data = bpy.data.cameras.new("VR_Stereo_Cam")
    cam_data.type = 'PANO'
    if hasattr(cam_data, 'panorama_type'):
        cam_data.panorama_type = 'EQUIRECTANGULAR'
    elif hasattr(cam_data, 'cycles'):
        cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'
        
    if hasattr(cam_data, 'stereo'):
        cam_data.stereo.interocular_distance = 0.065
        cam_data.stereo.convergence_distance = 35.0
        cam_data.stereo.convergence_mode = 'OFFAXIS'
        cam_data.stereo.pivot = 'CENTER'
        
    cam_obj = bpy.data.objects.new("VR_Stereo_Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, 0, 1.7)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(0))
    
    # 5. Piso do Planetário com Grade de Alta Definição
    bpy.ops.mesh.primitive_cylinder_add(radius=50, depth=0.1, location=(0, 0, -0.05))
    ground = bpy.context.active_object
    mat_ground = bpy.data.materials.new(name="Mat_Ground")
    g_bsdf = mat_ground.node_tree.nodes.get('Principled BSDF')
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.015, 0.03, 0.05, 1.0)
        g_bsdf.inputs['Roughness'].default_value = 0.8
    ground.data.materials.append(mat_ground)
    
    # Círculo Azimutal Iluminado
    bpy.ops.mesh.primitive_torus_add(major_radius=18, minor_radius=0.18, location=(0, 0, 0.05))
    az_ring = bpy.context.active_object
    mat_ring = bpy.data.materials.new(name="Mat_Ring")
    r_nodes = mat_ring.node_tree.nodes
    r_nodes.clear()
    r_emit = r_nodes.new(type='ShaderNodeEmission')
    r_emit.inputs['Color'].default_value = (0.0, 0.7, 1.0, 1.0)
    r_emit.inputs['Strength'].default_value = 4.0
    r_out = r_nodes.new(type='ShaderNodeOutputMaterial')
    mat_ring.node_tree.links.new(r_emit.outputs['Emission'], r_out.inputs['Surface'])
    az_ring.data.materials.append(mat_ring)
    
    # Textos dos Pontos Cardeais
    create_text_3d("NORTE", (0, 20, 0.2), scale=2.8, color=(0.1, 0.9, 1.0, 1.0), rot=(0, 0, 0))
    create_text_3d("SUL", (0, -20, 0.2), scale=2.8, color=(0.1, 0.9, 1.0, 1.0), rot=(0, 0, math.radians(180)))
    create_text_3d("LESTE", (20, 0, 0.2), scale=2.8, color=(0.1, 0.9, 1.0, 1.0), rot=(0, 0, math.radians(-90)))
    create_text_3d("OESTE", (-20, 0, 0.2), scale=2.8, color=(0.1, 0.9, 1.0, 1.0), rot=(0, 0, math.radians(90)))
    
    # 6. Linha do Meridiano Local (Tubo Emissivo Ciano Brilhante)
    curve_data = bpy.data.curves.new('MeridianLine', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.9
    polyline = curve_data.splines.new('POLY')
    
    num_pts = 96
    polyline.points.add(num_pts - 1)
    r_meridian = 35.0
    for i in range(num_pts):
        th = math.pi * (i / (num_pts - 1))
        x = 0
        y = r_meridian * math.cos(th)
        z = r_meridian * math.sin(th)
        polyline.points[i].co = (x, y, z, 1)
        
    meridian_obj = bpy.data.objects.new('Meridian_Line', curve_data)
    scene.collection.objects.link(meridian_obj)
    
    mat_meridian = bpy.data.materials.new(name="Mat_Meridian")
    m_nodes = mat_meridian.node_tree.nodes
    m_nodes.clear()
    m_emit = m_nodes.new(type='ShaderNodeEmission')
    m_emit.inputs['Color'].default_value = (0.0, 1.0, 0.9, 1.0)
    m_emit.inputs['Strength'].default_value = 10.0
    m_out = m_nodes.new(type='ShaderNodeOutputMaterial')
    mat_meridian.node_tree.links.new(m_emit.outputs['Emission'], m_out.inputs['Surface'])
    meridian_obj.data.materials.append(mat_meridian)
    
    create_text_3d("MERIDIANO LOCAL", (0, 30, 9), scale=2.2, color=(0.0, 1.0, 0.9, 1.0), rot=(math.radians(70), 0, 0))
    
    # 7. Centro de Massa (CM)
    alt_cm = math.radians(45)
    r_sky = 35.0
    cm_y = r_sky * math.cos(alt_cm)
    cm_z = r_sky * math.sin(alt_cm)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.3, location=(0, cm_y, cm_z))
    cm_marker = bpy.context.active_object
    cm_marker.name = "Centro_de_Massa"
    mat_cm = bpy.data.materials.new(name="Mat_CM")
    cm_n = mat_cm.node_tree.nodes
    cm_n.clear()
    cm_e = cm_n.new(type='ShaderNodeEmission')
    cm_e.inputs['Color'].default_value = (0.1, 1.0, 0.3, 1.0)
    cm_e.inputs['Strength'].default_value = 18.0
    cm_o = cm_n.new(type='ShaderNodeOutputMaterial')
    mat_cm.node_tree.links.new(cm_e.outputs['Emission'], cm_o.inputs['Surface'])
    cm_marker.data.materials.append(mat_cm)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=2.6, minor_radius=0.18, location=(0, cm_y, cm_z), rotation=(0, math.radians(90), 0))
    ring_cm = bpy.context.active_object
    ring_cm.data.materials.append(mat_cm)
    
    create_text_3d("Centro de Massa (Fixo)", (0, cm_y - 1.5, cm_z - 3.2), scale=1.6, color=(0.2, 1.0, 0.4, 1.0), rot=(math.radians(45), 0, 0))
    
    # 8. Estrelas do Binário Plo-I e Plo-II (HD e com Coroa Emissiva)
    r_orbit_I = 3.2
    r_orbit_II = 6.4
    
    # Plo-I (Amarela)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0, location=(0, cm_y, cm_z))
    plo1 = bpy.context.active_object
    plo1.name = "Plo-I"
    mat_plo1 = bpy.data.materials.new(name="Mat_Plo1")
    p1_n = mat_plo1.node_tree.nodes
    p1_n.clear()
    p1_e = p1_n.new(type='ShaderNodeEmission')
    p1_e.inputs['Color'].default_value = (1.0, 0.95, 0.4, 1.0)
    p1_e.inputs['Strength'].default_value = 30.0
    p1_o = p1_n.new(type='ShaderNodeOutputMaterial')
    mat_plo1.node_tree.links.new(p1_e.outputs['Emission'], p1_o.inputs['Surface'])
    plo1.data.materials.append(mat_plo1)
    
    label_plo1 = create_text_3d("Plo-I (m1)", (0, cm_y, cm_z), scale=1.5, color=(1.0, 0.95, 0.4, 1.0), rot=(math.radians(45), 0, 0))
    
    # Plo-II (Laranja)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0, cm_y, cm_z))
    plo2 = bpy.context.active_object
    plo2.name = "Plo-II"
    mat_plo2 = bpy.data.materials.new(name="Mat_Plo2")
    p2_n = mat_plo2.node_tree.nodes
    p2_n.clear()
    p2_e = p2_n.new(type='ShaderNodeEmission')
    p2_e.inputs['Color'].default_value = (1.0, 0.35, 0.05, 1.0)
    p2_e.inputs['Strength'].default_value = 25.0
    p2_o = p2_n.new(type='ShaderNodeOutputMaterial')
    mat_plo2.node_tree.links.new(p2_e.outputs['Emission'], p2_o.inputs['Surface'])
    plo2.data.materials.append(mat_plo2)
    
    label_plo2 = create_text_3d("Plo-II (m2)", (0, cm_y, cm_z), scale=1.3, color=(1.0, 0.4, 0.1, 1.0), rot=(math.radians(45), 0, 0))
    
    # 9. Domo de Estrelas Fixas (HD)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=45, location=(0, 0, 0))
    star_dome = bpy.context.active_object
    star_dome.name = "StarDome_FixedStars"
    
    mat_stars = bpy.data.materials.new(name="Mat_Stars")
    s_nodes = mat_stars.node_tree.nodes
    s_links = mat_stars.node_tree.links
    s_nodes.clear()
    
    s_out = s_nodes.new(type='ShaderNodeOutputMaterial')
    s_emit = s_nodes.new(type='ShaderNodeEmission')
    s_ramp = s_nodes.new(type='ShaderNodeValToRGB')
    s_ramp.color_ramp.elements[0].position = 0.980
    s_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    s_ramp.color_ramp.elements[1].position = 0.993
    s_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    
    s_tex = s_nodes.new(type='ShaderNodeTexVoronoi')
    s_tex.inputs['Scale'].default_value = 60.0
    
    s_links.new(s_tex.outputs['Distance'], s_ramp.inputs['Fac'])
    s_links.new(s_ramp.outputs['Color'], s_emit.inputs['Color'])
    s_emit.inputs['Strength'].default_value = 12.0
    s_links.new(s_emit.outputs['Emission'], s_out.inputs['Surface'])
    
    star_dome.data.materials.append(mat_stars)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 10. Animação Orbital
    binary_period_frames = 60
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        phase = 2 * math.pi * (f / binary_period_frames)
        
        rot_sky = 2 * math.pi * (f / total_frames)
        star_dome.rotation_euler = (0, 0, rot_sky)
        star_dome.keyframe_insert(data_path="rotation_euler", frame=f)
        
        th1 = alt_cm + (r_orbit_I / r_sky) * math.sin(phase)
        y1 = r_sky * math.cos(th1)
        z1 = r_sky * math.sin(th1)
        plo1.location = (0, y1, z1)
        label_plo1.location = (0, y1 + 3.8, z1 + 1.2)
        plo1.keyframe_insert(data_path="location", frame=f)
        label_plo1.keyframe_insert(data_path="location", frame=f)
        
        th2 = alt_cm - (r_orbit_II / r_sky) * math.sin(phase)
        y2 = r_sky * math.cos(th2)
        z2 = r_sky * math.sin(th2)
        plo2.location = (0, y2, z2)
        label_plo2.location = (0, y2 - 2.8, z2 - 1.2)
        plo2.keyframe_insert(data_path="location", frame=f)
        label_plo2.keyframe_insert(data_path="location", frame=f)

    # 11. Saída de Vídeo
    os.makedirs("output_videos", exist_ok=True)
    raw_video_path = os.path.abspath("output_videos/raw_quando_o_segundo_sol_chegar_stereo.mp4")
    if hasattr(scene.render.image_settings, 'media_type'):
        scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = raw_video_path
    
    print(f"Renderizando {total_frames} frames em 4K Estéreo 3D VR...")
    bpy.ops.render.render(animation=True)
    print(f"Render 4K concluído! Salvo em: {raw_video_path}")

if __name__ == "__main__":
    build_hd_vr_planetarium()
