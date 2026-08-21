# Antigravity Planetarium & IOAA VR Simulator

Este ambiente foi estruturado para resolver automaticamente questões de olimpíadas de astronomia (como IOAA e OBA) e gerar simulações 3D imersivas em vídeo para **óculos de Realidade Virtual (VR 360° Equirectangular)**.

---

## 📁 Estrutura do Workspace

* [`.agent/rules`](file:///.agent/rules): Regras globais de física, padrões de câmera VR 360°, resoluções e FPS.
* [`.agent/skills/ioaa-solver/SKILL.md`](file:///.agent/skills/ioaa-solver/SKILL.md): Instruções de modelagem de problemas de mecânica celeste e efemérides.
* [`.agent/skills/vr-blender-engine/SKILL.md`](file:///.agent/skills/vr-blender-engine/SKILL.md): Templates e parâmetros para renderização de cenas no Blender em modo headless.
* [`input_provas/`](file:///input_provas/): Pasta para armazenar os enunciados/provas da IOAA.
* [`scripts/`](file:///scripts/): Scripts Python e de renderização (`sample_orbit_sim.py`, `spatial_media_metadata.py`).
* [`output_videos/`](file:///output_videos/): Destino dos vídeos MP4 finais com metadados 360° VR injetados.

---

## 🚀 Como Usar

1. Salve sua questão em [`input_provas/`](file:///input_provas/).
2. Peça ao **Antigravity**:
   > *"Resolva a questão da IOAA em `input_provas/...` e gere o vídeo 360° VR."*
3. O agente fará a dedução física, gerará o script do Blender, renderizará em background e injetará os metadados esféricos em [`output_videos/`](file:///output_videos/).
