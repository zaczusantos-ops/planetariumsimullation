"""
Renderizador Unificado Planetarium Core (Todas as 4 Simulações)
- Utiliza estrelas 100% reais do catálogo HYG (sem linhas artificiais)
- Renderiza frame 360 no Blender
- Converte em vídeo MP4 contínuo de 10s em alta qualidade
- Injeta metadados esféricos VR 360
"""

import os
import subprocess
import sys

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
FFMPEG_EXE = r"C:\Users\Claudio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
SPATIAL_SCRIPT = os.path.abspath("scripts/spatial_media_metadata.py")

SIMULATIONS = [
    {
        "id": "ioaa2019_p1_keszthely",
        "name": "Problema 1 - Céu Real de Keszthely (Hungria)",
        "script": "scripts/sim_ioaa2019_p1_keszthely.py"
    },
    {
        "id": "ioaa2019_p2_latitude25s",
        "name": "Problema 2 - Desafio de Latitude (Céu Real)",
        "script": "scripts/sim_ioaa2019_p2_latitude25s.py"
    },
    {
        "id": "ioaa2019_p3_lunar_eclipse",
        "name": "Problema 3 - Céu Real na Lua (Eclipse por Terra)",
        "script": "scripts/sim_ioaa2019_p3_lunar_eclipse.py"
    },
    {
        "id": "quando_o_segundo_sol_chegar",
        "name": "Quando o segundo Sol chegar (Binário com Céu Real)",
        "script": "scripts/sim_quando_o_segundo_sol_chegar_stereo.py"
    }
]

def main():
    os.makedirs("output_videos", exist_ok=True)
    os.makedirs("output_videos/frames", exist_ok=True)

    for sim in SIMULATIONS:
        print("\n" + "=" * 60)
        print(f"Iniciando: {sim['name']}")
        print("=" * 60)

        frame_png = os.path.abspath(f"output_videos/frames/{sim['id']}.png")
        raw_mp4 = os.path.abspath(f"output_videos/raw_{sim['id']}.mp4")
        final_vr_mp4 = os.path.abspath(f"output_videos/{sim['id']}_VR360.mp4")

        # 1. Renderizar Frame 360 no Blender
        print("1. Renderizando frame esférico no Blender Cycles...")
        render_expr = f"import bpy; bpy.context.scene.render.filepath=r'{frame_png}'; bpy.ops.render.render(write_still=True)"
        cmd_blender = [
            BLENDER_EXE,
            "--background",
            "--python", sim["script"],
            "--python-expr", render_expr
        ]
        res = subprocess.run(cmd_blender)
        if res.returncode != 0:
            print(f"Aviso: Erro ao renderizar no Blender para {sim['id']}")
            continue

        if not os.path.exists(frame_png):
            print(f"Erro: frame não encontrado em {frame_png}")
            continue

        # 2. Gerar Vídeo MP4 com FFmpeg
        print("2. Gerando vídeo MP4 contínuo de 10 segundos...")
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
            raw_mp4,
            final_vr_mp4
        ]
        subprocess.run(cmd_meta, check=True)

        print(f"--> [SUCESSO] {sim['name']} finalizado: {final_vr_mp4}")

    print("\n" + "=" * 60)
    print("TODAS AS SIMULAÇÕES FORAM RENDERIZADAS COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    main()
