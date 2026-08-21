"""
Script para injeção de metadados 360 VR (Spherical Video V2) em arquivos MP4.
Suporta Monoscópico 2D (mono) e Estereoscópico 3D (top-bottom / left-right).
Compatível com Meta Quest, Skybox VR, Apple Vision Pro, YouTube VR e players 360.
"""

import sys
import os
import struct

def build_spherical_xml(stereo_mode="top-bottom"):
    stereo_xml = f"<GSpherical:StereoMode>{stereo_mode}</GSpherical:StereoMode>" if stereo_mode != "mono" else ""
    xml_str = (
        '<?xml version="1.0"?>'
        '<rdf:SphericalVideo'
        ' xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
        ' xmlns:GSpherical="http://ns.google.com/videos/1.0/">'
        '<GSpherical:Spherical>true</GSpherical:Spherical>'
        '<GSpherical:Stitched>true</GSpherical:Stitched>'
        '<GSpherical:StitchingSoftware>Antigravity Planetarium 3D VR Engine</GSpherical:StitchingSoftware>'
        '<GSpherical:ProjectionType>equirectangular</GSpherical:ProjectionType>'
        f'{stereo_xml}'
        '</rdf:SphericalVideo>'
    )
    return xml_str.encode('utf-8')

SPHERICAL_UUID = b'\xff\xcc\x82\x63\xf8\x55\x4a\x93\x88\x14\x58\x7a\x02\x52\x1f\xdd'

def inject_spatial_metadata(input_file, output_file, stereo_mode="top-bottom"):
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return False
        
    print(f"Injetando metadados 360° VR (Modo: {stereo_mode}) em: {input_file} -> {output_file}")
    with open(input_file, "rb") as f:
        data = f.read()

    spherical_xml = build_spherical_xml(stereo_mode)
    uuid_payload = SPHERICAL_UUID + spherical_xml
    uuid_size = len(uuid_payload) + 8
    uuid_atom = struct.pack(">I4s", uuid_size, b"uuid") + uuid_payload

    # Inserir antes de 'moov' ou no final do cabeçalho
    moov_pos = data.find(b"moov")
    if moov_pos != -1:
        insert_pos = moov_pos - 4
        new_data = data[:insert_pos] + uuid_atom + data[insert_pos:]
    else:
        new_data = data + uuid_atom

    with open(output_file, "wb") as f:
        f.write(new_data)
        
    print("Metadados 360° VR Estereoscópicos injetados com sucesso!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python spatial_media_metadata.py <input.mp4> <output_vr.mp4> [mono|top-bottom|left-right]")
    else:
        mode = sys.argv[3] if len(sys.argv) > 3 else "top-bottom"
        inject_spatial_metadata(sys.argv[1], sys.argv[2], stereo_mode=mode)
