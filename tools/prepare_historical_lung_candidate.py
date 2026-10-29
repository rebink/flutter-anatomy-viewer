"""Build an isolated, unregistered 2008-lung/4.0-body preview, never app assets.

First run prepare_official_anatomy.py and check_asset_licenses.py. Use the same
trimesh environment. Historical inputs must already be in the review cache.
"""
import base64
import hashlib
import html
import io
import json
import shutil
import zipfile
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.research/bodyparts3d-4.0-candidate'
CACHE = ROOT / '.research/bodyparts3d-20080812-review'
OUT = ROOT / '.research/bodyparts3d-historical-lung-candidate'
ARCHIVE = 'BodyParts3D-stl-0.01.zip'
ARCHIVE_HASH = 'e0b45ac0ba507fb87e3869f1df2b91b1bc8416907d49c2b36e7c9a1485af8d71'
LUNGS = {
    'lung_right': ['FMA7333', 'FMA7337', 'FMA7383'],
    'lung_left': ['FMA7370', 'FMA7371'],
}


def main():
    archive_bytes = (CACHE / ARCHIVE).read_bytes()
    if hashlib.sha256(archive_bytes).hexdigest() != ARCHIVE_HASH:
        raise ValueError('Historical source checksum mismatch; source review required')
    provenance_bytes = (BASE / 'anatomy-provenance.json').read_bytes()
    original = json.loads(provenance_bytes)
    for name in ('anatomy.glb', 'anatomy-data.js', 'anatomy-manifest.json'):
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != original['artifacts'][name]:
            raise ValueError(f'Base candidate checksum mismatch: {name}')
    scene = trimesh.load(BASE / 'anatomy.glb', force='scene')
    manifest = json.loads((BASE / 'anatomy-manifest.json').read_text())
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for name, concepts in LUNGS.items():
            lobes = [trimesh.load_mesh(io.BytesIO(archive.read(f'stl/{concept}.stl')),
                                      file_type='stl') for concept in concepts]
            assert all(mesh.is_watertight and len(mesh.faces) for mesh in lobes)
            mesh = trimesh.util.concatenate(lobes)
            # Unit/axis conversion only: cross-release anatomical alignment is unapproved.
            mesh.vertices = mesh.vertices[:, [0, 2, 1]] / 1000
            mesh.vertices[:, 2] *= -1
            scene.delete_geometry(name)
            scene.add_geometry(mesh, node_name=name, geom_name=name)
            manifest[name] = {
                'release': '20080812', 'concepts': concepts,
                'parts': [f'stl/{concept}.stl' for concept in concepts],
                'triangles': len(mesh.faces), 'bounds': mesh.bounds.tolist(),
                'registration': 'none; axis and unit conversion only',
            }
    assert set(scene.geometry) == set(manifest)
    blob = scene.export(file_type='glb')
    restored = trimesh.load(io.BytesIO(blob), file_type='glb', force='scene')
    assert set(restored.geometry) == set(manifest)
    for name in LUNGS:
        assert len(restored.geometry[name].faces) == manifest[name]['triangles']
    artifacts = {
        'anatomy.glb': blob,
        'anatomy-data.js': ('window.ANATOMY_GLB = "' + base64.b64encode(blob).decode() + '";\n').encode(),
        'anatomy-manifest.json': (json.dumps(manifest, indent=2) + '\n').encode(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in artifacts.items():
        (OUT / name).write_bytes(data)
    provenance = {
        'status': 'review only; not approved for production',
        'license_scope': 'Current database-wide CC BY 4.0 statement; historical README retains CC BY-SA 2.1 JP. Historical-release scope not resolved.',
        'official_license_url': 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html',
        'historical_readme_url': 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20080812/README-ja.html',
        'base_provenance': original,
        'base_provenance_sha256': hashlib.sha256(provenance_bytes).hexdigest(),
        'historical_source': {
            'url': 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20080812/' + ARCHIVE,
            'sha256': ARCHIVE_HASH,
        },
        'registration': 'No translation, scaling to fit, or anatomical registration applied.',
        'modifications': 'Combined five historical STL lobes into two lungs; converted Z-up mm to Y-up m; replaced candidate lung meshes; exported GLB/base64. No further lung decimation.',
        'artifacts': {name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()},
    }
    (OUT / 'anatomy-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    credits = ('RELEASE 4.0 COMPONENTS (EXCLUDING REPLACEMENT LUNGS)\n'
               + (BASE / 'CREDITS.txt').read_text() + '\nHISTORICAL LUNG REVIEW CANDIDATE\n'
               'BodyParts3D, Copyright 2008 The Database Center for Life Science.\n'
               + provenance['license_scope'] + '\n'
               + provenance['official_license_url'] + '\n'
               + provenance['historical_readme_url'] + '\n'
               + provenance['historical_source']['url'] + '\n'
               + 'Modifications: ' + provenance['modifications'] + '\n'
               + 'Not clinically validated. Cross-release alignment is not approved.\n'
               + 'Three.js: MIT; see THREE_LICENSE.txt.\n')
    (OUT / 'CREDITS.txt').write_text(credits)
    (OUT / 'BODY_PARTS_LICENSE.txt').write_text(
        (BASE / 'BODY_PARTS_LICENSE.txt').read_text()
        + '\nHistorical lung scope caveat:\n' + provenance['license_scope']
        + '\nhttps://creativecommons.org/licenses/by-sa/2.1/jp/legalcode\n'
        + provenance['historical_readme_url'] + '\n')
    for name in ('viewer.js', 'THREE_LICENSE.txt'):
        shutil.copyfile(ROOT / 'assets/viewer' / name, OUT / name)
    page = (ROOT / 'assets/viewer/index.html').read_text()
    panel = '''<aside style="position:absolute;z-index:2;top:8px;left:8px;right:8px;padding:12px;background:white;font:14px sans-serif">
<strong>Historical lung candidate: alignment and license scope under review.</strong>
<p>16 organ regions only. No muscle/bone coverage. Not approved for production.</p>
<button data-focus="lung_right">Right lung</button> <button data-focus="lung_left">Left lung</button> <button data-focus="heart">Heart</button> <button data-focus="">Whole body</button>
<details><summary>Credits and licenses</summary><pre style="white-space:pre-wrap;max-height:30vh;overflow:auto">'''
    panel += html.escape(credits) + '</pre><a href="THREE_LICENSE.txt">Three.js license</a></details></aside>'
    page = page.replace('<body>', '<body>' + panel)
    page = page.replace('</body>', '<script src="preview-controls.js"></script></body>')
    (OUT / 'index.html').write_text(page)
    (OUT / 'preview-controls.js').write_text(
        "document.querySelectorAll('[data-focus]').forEach(button => button.addEventListener('click', () => {"
        "if (!window.anatomy?.ready) return; window.anatomy.configure({reducedMotion:true,loading:false});"
        "button.dataset.focus ? window.anatomy.focus(button.dataset.focus) : window.anatomy.reset();}));\n")
    print(f'PASS: source hashes, watertight lobes and GLB round-trip; candidate at {OUT}')


if __name__ == '__main__':
    main()
