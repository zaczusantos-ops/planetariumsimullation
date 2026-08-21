"""
Pipeline Automatizado: Renderiza simulação no Blender e injeta Metadados VR 360°.
"""

import os
import subprocess
import sys

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def run_simulation(script_path):
    print(f"=== 1. Renderizando Simulação: {script_path} ===")
    cmd = [BLENDER_PATH, "-b", "-P", script_path]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("Erro durante a renderização no Blender.")
        return False
    return True

def inject_metadata(raw_mp4, final_vr_mp4):
    print(f"=== 2. Injetando Metadados VR 360° ===")
    from spatial_media_metadata import inject_spatial_metadata
    return inject_spatial_metadata(raw_mp4, final_vr_mp4)

if __name__ == "__main__":
    script = sys.argv[1] if len(sys.argv) > 1 else "scripts/sim_quando_o_segundo_sol_chegar.py"
    raw_video = "output_videos/raw_quando_o_segundo_sol_chegar.mp4"
    final_video = "output_videos/quando_o_segundo_sol_chegar_VR360.mp4"
    
    if os.path.exists(raw_video):
        inject_metadata(raw_video, final_video)
        print(f"Vídeo VR 360° gerado com sucesso em: {final_video}")
    else:
        if run_simulation(script):
            inject_metadata(raw_video, final_video)
            print(f"Vídeo VR 360° pronto: {final_video}")
