"""
Renderizador Ultra-Rápido das Simulações IOAA 2019
- Renderiza 1 frame estático equirretangular em alta qualidade (Cycles 24 samples)
- Converte em vídeo contínuo de 10 segundos via FFmpeg
- Injeta metadados esféricos de Realidade Virtual 360°
"""

import subprocess
import os
import sys

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FFMPEG_EXE = r"C:\Users\Claudio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
SPATIAL_SCRIPT = os.path.abspath("scripts/spatial_media_metadata.py")

SIMULATIONS = [
    {
        "id": "ioaa2019_p1_keszthely",
        "name": "Problema 1 - Keszthely à Meia-Noite",
        "script": "scripts/sim_ioaa2019_p1_keszthely.py"
    },
    {
        "id": "ioaa2019_p2_latitude25s",
        "name": "Problema 2 - Latitude 25° Sul",
        "script": "scripts/sim_ioaa2019_p2_latitude25s.py"
    },
    {
        "id": "ioaa2019_p3_lunar_eclipse",
        "name": "Problema 3 - Eclipse Lunar em Mare Fecunditatis",
        "script": "scripts/sim_ioaa2019_p3_lunar_eclipse.py"
    }
]

def render_all():
    os.makedirs("output_videos", exist_ok=True)
    os.makedirs("output_videos/frames", exist_ok=True)

    for sim in SIMULATIONS:
        print("\n" + "=" * 60)
        print(f"Processando: {sim['name']}")
        print("=" * 60)

        frame_png = os.path.abspath(f"output_videos/frames/{sim['id']}.png")
        raw_mp4 = os.path.abspath(f"output_videos/raw_{sim['id']}.mp4")
        final_vr_mp4 = os.path.abspath(f"output_videos/{sim['id']}_VR360.mp4")

        # 1. Renderizar 1 Frame PNG no Blender
        print("1. Renderizando frame esférico 360 no Blender...")
        render_expr = f"import bpy; bpy.context.scene.render.filepath=r'{frame_png}'; bpy.ops.render.render(write_still=True)"
        cmd_blender = [
            BLENDER_EXE,
            "--background",
            "--python", sim["script"],
            "--python-expr", render_expr
        ]
        subprocess.run(cmd_blender, check=True)

        if not os.path.exists(frame_png):
            print(f"Erro: frame não encontrado em {frame_png}")
            continue

        # 2. Gerar Vídeo MP4 de 10 segundos com FFmpeg
        print("2. Gerando vídeo MP4 de 10 segundos com FFmpeg...")
        cmd_ffmpeg = [
            FFMPEG_EXE,
            "-y",
            "-loop", "1",
            "-i", frame_png,
            "-c:v", "libx264",
            "-t", "10",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=2048:1024",
            raw_mp4
        ]
        subprocess.run(cmd_ffmpeg, check=True)

        # 3. Injetar Metadados Espaciais VR 360
        print("3. Injetando metadados esféricos VR 360...")
        cmd_meta = [
            sys.executable,
            SPATIAL_SCRIPT,
            "-i", raw_mp4,
            final_vr_mp4
        ]
        subprocess.run(cmd_meta, check=True)

        print(f"--> [SUCESSO] {sim['name']} gerado: {final_vr_mp4}")

    print("\n" + "=" * 60)
    print("TODAS AS 3 SIMULAÇÕES FORAM RENDERIZADAS E FINALIZADAS COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    render_all()
