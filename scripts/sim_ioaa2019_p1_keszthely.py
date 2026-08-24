"""
Simulação IOAA 2019 - Problema 1: Céu de Keszthely (Hungria) à Meia-Noite
- Latitude: 46.77° N
- Tempo Sideral Local (LST): 01h 00m (Gama Cassiopeiae culminando no meridiano superior)
- 3 Novas de 2ª magnitude destacadas
- Aglomerados Globulares de Messier: M2, M13, M15, M30, M56, M71, M72, M92
- Câmera 360° Equiretangular para VR Cardboard
"""

import bpy
import math
import numpy as np
import os

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FFMPEG_EXE = r"C:\Users\Claudio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"

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
    scene.frame_end = 90  # 3 segundos para teste / loop suave

    scene.render.image_settings.media_type = 'IMAGE'
    scene.render.image_settings.file_format = 'PNG'
    
    # Câmera 360 Panorâmica Equiretangular
    cam_data = bpy.data.cameras.new("VR_Camera_360")
    cam_data.type = 'PANO'
    cam_data.panorama_type = 'EQUIRECTANGULAR'
    
    cam_obj = bpy.data.objects.new("VR_Camera_360", cam_data)
    cam_obj.location = (0, 0, 1.7)  # Altura dos olhos do observador
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-90)) # Olhando para o Norte
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Fundo do Espaço
    world = bpy.data.worlds.new("CosmicWorld")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.002, 0.004, 0.01, 1.0)
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

def build_keszthely_sky():
    scene = setup_scene()
    
    # Materiais
    star_mat = create_emission_mat("StarMat", (0.9, 0.95, 1.0, 1.0), strength=4.0)
    bright_star_mat = create_emission_mat("BrightStarMat", (1.0, 1.0, 1.0, 1.0), strength=8.0)
    nova_mat = create_emission_mat("NovaMat", (1.0, 0.2, 0.1, 1.0), strength=12.0) # Novas avermelhadas brilhantes
    cluster_mat = create_emission_mat("ClusterMat", (0.2, 0.8, 1.0, 1.0), strength=6.0) # Aglomerados azulados
    grid_mat = create_emission_mat("GridMat", (0.0, 0.5, 0.7, 1.0), strength=1.5)
    
    # Domo de estrelas de fundo (1000 estrelas)
    np.random.seed(42)
    R = 80.0
    phi_stars = np.random.uniform(0, 2*np.pi, 800)
    theta_stars = np.arccos(np.random.uniform(-1, 1, 800))
    
    mesh = bpy.data.meshes.new("StarsMesh")
    obj = bpy.data.objects.new("StarsDome", mesh)
    scene.collection.objects.link(obj)
    
    # Gerar campo de estrelas procedural
    for i in range(500):
        u = np.random.uniform(0, 1)
        v = np.random.uniform(0, 1)
        az = 2 * math.pi * u
        alt = math.asin(2 * v - 1)
        
        if alt > 0.05: # Acima do horizonte
            x = R * math.cos(alt) * math.sin(az)
            y = R * math.cos(alt) * math.cos(az)
            z = R * math.sin(alt)
            
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15 + 0.1*np.random.rand(), location=(x, y, z))
            star = bpy.context.active_object
            star.data.materials.append(star_mat)

    # 1. Gama Cassiopeiae culminando no meridiano Norte a alta altitude (~70°)
    # Localização de Cassiopeia: Az ~ 0° (Norte), Alt ~ 73°
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.6, location=(0, R * math.cos(math.radians(73)), R * math.sin(math.radians(73))))
    gamma_cas = bpy.context.active_object
    gamma_cas.name = "Gamma_Cassiopeiae"
    gamma_cas.data.materials.append(bright_star_mat)

    # 2. As 3 Novas de 2ª magnitude destacadas
    novae_coords = [
        ("Nova_1_Pegasus", math.radians(45), math.radians(65)),    # Próximo a Pegasus
        ("Nova_2_Cygnus", math.radians(310), math.radians(55)),    # Próximo a Cygnus
        ("Nova_3_Auriga", math.radians(70), math.radians(35)),     # Próximo a Auriga
    ]
    for name, az, alt in novae_coords:
        x = R * math.cos(alt) * math.sin(az)
        y = R * math.cos(alt) * math.cos(az)
        z = R * math.sin(alt)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.8, location=(x, y, z))
        nova = bpy.context.active_object
        nova.name = name
        nova.data.materials.append(nova_mat)
        
        # Círculo indicador ao redor da Nova
        bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.08, location=(x, y, z))
        ring = bpy.context.active_object
        ring.data.materials.append(nova_mat)

    # 3. Aglomerados Globulares de Messier (M2, M13, M15, M30, M56, M71, M72, M92)
    clusters = [
        ("M13_Hercules", math.radians(285), math.radians(30)),
        ("M92_Hercules", math.radians(300), math.radians(40)),
        ("M15_Pegasus", math.radians(110), math.radians(50)),
        ("M2_Aquarius", math.radians(140), math.radians(30)),
        ("M56_Lyra", math.radians(315), math.radians(60)),
        ("M71_Sagitta", math.radians(270), math.radians(45)),
    ]
    for name, az, alt in clusters:
        x = R * math.cos(alt) * math.sin(az)
        y = R * math.cos(alt) * math.cos(az)
        z = R * math.sin(alt)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.5, location=(x, y, z))
        cl = bpy.context.active_object
        cl.name = name
        cl.data.materials.append(cluster_mat)

    # 4. Linha Meridiana Brilhante (Norte - Zênite - Sul)
    curve_data = bpy.data.curves.new('MeridianLine', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(30)
    for idx, angle_deg in enumerate(np.linspace(0, 180, 31)):
        ang = math.radians(angle_deg)
        # De Norte (y=R) passando pelo Zênite (z=R) até Sul (y=-R)
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
    ground_mat = create_emission_mat("GroundMat", (0.01, 0.02, 0.03, 1.0), strength=0.2)
    ground.data.materials.append(ground_mat)

    # Output path
    os.makedirs("output_videos", exist_ok=True)
    scene.render.filepath = os.path.abspath("output_videos/raw_ioaa2019_p1_keszthely.mp4")

if __name__ == "__main__":
    build_keszthely_sky()
