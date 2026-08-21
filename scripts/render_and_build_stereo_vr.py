"""
Pipeline Completo: Renderiza Stereo 3D no Blender, empilha L/R via FFmpeg e injeta Metadados Estéreo 3D VR.
"""

import os
import subprocess
import sys

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FFMPEG_PATH = r"C:\Users\Claudio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"

def run_pipeline():
    os.makedirs("output_videos", exist_ok=True)
    
    # 1. Renderizar no Blender
    print("=== Passo 1/3: Renderizando cena no Blender em modo Estéreo 3D ===")
    cmd_blender = [BLENDER_PATH, "-b", "-P", "scripts/sim_quando_o_segundo_sol_chegar_stereo.py"]
    res = subprocess.run(cmd_blender)
    if res.returncode != 0:
        print("Erro na renderização do Blender.")
        return False
        
    left_video = "output_videos/raw_quando_o_segundo_sol_chegar_stereo_L.mp4"
    right_video = "output_videos/raw_quando_o_segundo_sol_chegar_stereo_R.mp4"
    stacked_video = "output_videos/raw_quando_o_segundo_sol_chegar_stereo_stacked.mp4"
    final_vr_3d = "output_videos/quando_o_segundo_sol_chegar_STEREO_3D_VR.mp4"
    
    # 2. Empilhar L/R em Top-Bottom com FFmpeg
    print("=== Passo 2/3: Empilhando canais esquerdo e direito (Top-Bottom 3D) ===")
    if os.path.exists(stacked_video):
        os.remove(stacked_video)
        
    cmd_ffmpeg = [
        FFMPEG_PATH, "-y",
        "-i", left_video,
        "-i", right_video,
        "-filter_complex", "vstack",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        stacked_video
    ]
    res_ff = subprocess.run(cmd_ffmpeg)
    if res_ff.returncode != 0:
        print("Erro ao empilhar canais estéreo com FFmpeg.")
        return False
        
    # 3. Injetar Metadados Estéreo 360 VR (top-bottom)
    print("=== Passo 3/3: Injetando metadados espaciais Estéreo 3D VR ===")
    from spatial_media_metadata import inject_spatial_metadata
    inject_spatial_metadata(stacked_video, final_vr_3d, stereo_mode="top-bottom")
    
    print(f"\n[SUCESSO] Video 3D Estereoscopico VR 360 gerado com sucesso em: {final_vr_3d}")
    return True

if __name__ == "__main__":
    run_pipeline()
