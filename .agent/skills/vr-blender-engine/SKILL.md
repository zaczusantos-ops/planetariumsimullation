---
name: vr-blender-engine
description: Templates e boas práticas para geração e renderização de cenas 360° VR no Blender em modo headless
---

# VR Blender Engine Skill

Instruções para geração automatizada de scripts Python (`bpy`) para o Blender voltados para visualização imersiva em Realidade Virtual (VR).

## Configuração da Câmera Panorâmica 360°
```python
import bpy

scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # Cycles suporta câmera panorâmica equiretangular nativamente

# Criação da câmera esférica 360
cam_data = bpy.data.cameras.new("VR_Camera_360")
cam_data.type = 'PANO'
cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'

cam_obj = bpy.data.objects.new("VR_Camera_360", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
```

## Diretrizes Visuais para VR
1. **Conforto Visual**: Evitar movimentos bruscos de aceleração de câmera. Se o observador estiver fixo (planeta/planetário), manter a câmera estável.
2. **Escala e Iluminação**:
   - Estrelas com shader de emissão (`Emission` com força alta) e ponto de luz `POINT`/`SUN`.
   - Fundo cósmico com imagem HDRI da Via Láctea ou gerador procedural de estrelas no World Shader.
3. **Resoluções**:
   - Teste rápido: 1920x960 @ 30 fps (5 segundos = 150 frames).
   - Produção: 3840x1920 @ 60 fps (10-30 segundos).
