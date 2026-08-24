"""
Script de automação para renderizar os 3 vídeos da IOAA 2019 no Blender e injetar metadados VR 360.
"""

import subprocess
import os
import sys

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SPATIAL_SCRIPT = os.path.abspath("scripts/spatial_media_metadata.py")

SIMULATIONS = [
    {
        "name": "Problema 1 - Keszthely à Meia-Noite",
        "script": "scripts/sim_ioaa2019_p1_keszthely.py",
        "raw_video": "output_videos/raw_ioaa2019_p1_keszthely.mp4",
        "final_video": "output_videos/ioaa2019_p1_keszthely_VR360.mp4"
    },
    {
        "name": "Problema 2 - Latitude 25° Sul",
        "script": "scripts/sim_ioaa2019_p2_latitude25s.py",
        "raw_video": "output_videos/raw_ioaa2019_p2_latitude25s.mp4",
        "final_video": "output_videos/ioaa2019_p2_latitude25s_VR360.mp4"
    },
    {
        "name": "Problema 3 - Eclipse Lunar em Mare Fecunditatis",
        "script": "scripts/sim_ioaa2019_p3_lunar_eclipse.py",
        "raw_video": "output_videos/raw_ioaa2019_p3_lunar_eclipse.mp4",
        "final_video": "output_videos/ioaa2019_p3_lunar_eclipse_VR360.mp4"
    }
]

def render_and_process():
    os.makedirs("output_videos", exist_ok=True)

    for sim in SIMULATIONS:
        print("\n" + "=" * 60)
        print(f"Iniciando Renderização: {sim['name']}")
        print("=" * 60)

        cmd_blender = [
            BLENDER_EXE,
            "--background",
            "--python", sim["script"],
            "--render-anim"
        ]

        print("Executando Blender headless...")
        res = subprocess.run(cmd_blender)
        if res.returncode != 0:
            print(f"Erro ao renderizar {sim['name']}")
            continue

        print(f"Injetando metadados esféricos VR 360 em {sim['final_video']}...")
        cmd_meta = [
            sys.executable,
            SPATIAL_SCRIPT,
            "-i", sim["raw_video"],
            sim["final_video"]
        ]
        subprocess.run(cmd_meta)
        print(f"[OK] {sim['name']} gerado com sucesso!")

    print("\n" + "=" * 60)
    print("TODAS AS 3 SIMULAÇÕES FORAM RENDERIZADAS COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    render_and_process()
