"""Rebuild exclusively from official BodyParts3D Release 4.0 (CC BY 4.0).

Run in a venv with trimesh==5.1.1 and fast-simplification==0.2.0 installed.
No previous meshes or third-party mirror caches are reused.
"""
import base64
import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
SOURCES = {
    'isa_BP3D_4.0_obj_99.zip': '40665852c49f218326590e204db91064a1ecfc3c6f8cbd7bbbcaac62c7cd409e',
    'isa_element_parts.txt': 'a3de74423f943b0d724ae8f59b3a817f87c423a544f8db98113b1980817cbeaf',
    'partof_element_parts.txt': '3f5f6df1028eb122b30de77c711597b6bb8e5541658e5985859fd228adbf88ea',
}
# Explicit trees: PART-OF includes constituent structures; IS-A groups similar parts.
PARTS = {
    'body_shell': ('isa', ['FMA7163']),
    'lung_right': ('partof', ['FMA7309']),
    'lung_left': ('partof', ['FMA7310']),
    'heart': ('isa', ['FMA86212']),
    'liver': ('partof', ['FMA7197']),
    'stomach': ('isa', ['FMA7148']),
    'brain': ('partof', ['FMA50801']),
    'airway': ('isa', ['FMA7394', 'FMA7409']),
    'esophagus': ('isa', ['FMA7131']),
    'small_intestine': ('partof', ['FMA7206', 'FMA7207', 'FMA7208']),
    'large_intestine': ('partof', ['FMA7201']),
    'kidney_left': ('isa', ['FMA7205']),
    'kidney_right': ('isa', ['FMA7204']),
    'bladder': ('isa', ['FMA15900']),
    'pancreas': ('partof', ['FMA7198']),
    'gallbladder': ('isa', ['FMA7202']),
}


def fetch(name, expected_hash, cache):
    path = cache / name
    if not path.exists():
        temporary = path.with_suffix(path.suffix + '.download')
        with urllib.request.urlopen(BASE + name, timeout=120) as response, temporary.open('wb') as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
        temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f'Source checksum mismatch: {path}; do not silently accept changed upstream data')
    return path


def main():
    cache = ROOT / '.research' / 'bodyparts3d-4.0-official'
    cache.mkdir(parents=True, exist_ok=True)
    paths = {name: fetch(name, digest, cache) for name, digest in SOURCES.items()}
    mappings = {}
    for tree in ['isa', 'partof']:
        mapping = {}
        with paths[f'{tree}_element_parts.txt'].open() as source:
            rows = csv.reader(source, delimiter='\t')
            next(rows)
            for concept, _name, element in rows:
                mapping.setdefault(concept, set()).add(element)
        mappings[tree] = mapping

    scene = trimesh.Scene()
    manifest = {}
    with zipfile.ZipFile(paths['isa_BP3D_4.0_obj_99.zip']) as archive:
        members = {Path(name).stem: name for name in archive.namelist() if name.endswith('.obj')}
        for name, (tree, concepts) in PARTS.items():
            ids = sorted(set().union(*(mappings[tree][concept] for concept in concepts)))
            meshes = [trimesh.load_mesh(io.BytesIO(archive.read(members[part])), file_type='obj') for part in ids]
            mesh = trimesh.util.concatenate(meshes)
            target = 24000 if name in ['body_shell', 'brain'] else 8000
            if len(mesh.faces) > target:
                mesh = mesh.simplify_quadric_decimation(face_count=target)
            # Official coordinates are shared Z-up millimetres; viewer uses Y-up metres.
            mesh.vertices = mesh.vertices[:, [0, 2, 1]] / 1000
            mesh.vertices[:, 2] *= -1
            scene.add_geometry(mesh, node_name=name, geom_name=name)
            manifest[name] = {'tree': tree, 'concepts': concepts, 'parts': ids,
                              'triangles': len(mesh.faces), 'bounds': mesh.bounds.tolist()}
            print(name, len(ids), 'source elements;', len(mesh.faces), 'triangles', flush=True)

    # Keep the candidate out of the app until the changed lung geometry is approved.
    output = ROOT / '.research' / 'bodyparts3d-4.0-candidate'
    output.mkdir(parents=True, exist_ok=True)
    blob = scene.export(file_type='glb')
    embedded = ('window.ANATOMY_GLB = "' + base64.b64encode(blob).decode() + '";\n').encode()
    manifest_data = (json.dumps(manifest, indent=2) + '\n').encode()
    artifacts = {'anatomy.glb': blob, 'anatomy-data.js': embedded, 'anatomy-manifest.json': manifest_data}
    provenance = {
        'database': 'BodyParts3D', 'release': '4.0', 'license': 'CC-BY-4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'official_license_url': 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html',
        'license_updated': '2025-02-27',
        'sources': [{'url': BASE + name, 'sha256': digest} for name, digest in SOURCES.items()],
        'artifacts': {name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()},
        'modifications': 'Combined official OBJ elements, reduced polygons, converted coordinates/units, exported GLB and base64 JS; illustrative runtime materials.',
    }
    for name, data in artifacts.items():
        (output / name).write_bytes(data)
    (output / 'anatomy-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    evidence = ROOT / 'docs' / 'licensing' / 'bodyparts3d'
    for source, target in [('CANDIDATE_CREDITS.txt', 'CREDITS.txt'),
                           ('CANDIDATE_LICENSE.txt', 'BODY_PARTS_LICENSE.txt')]:
        (output / target).write_bytes((evidence / source).read_bytes())
    print('GLB bytes:', len(blob))


if __name__ == '__main__':
    main()
