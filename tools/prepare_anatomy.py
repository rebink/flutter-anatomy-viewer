"""Build attributed, reduced-detail BodyParts3D meshes; not clinical validation.

Run in a venv with trimesh==5.1.1 and fast-simplification==0.2.0 installed.
This legacy build remains CC BY-SA 2.1 Japan. The separate official-source
candidate builder is prepare_official_anatomy.py; do not mix their outputs.
"""
import base64
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/f0eeb6e843380cfe6b83797cf8c3e1af74de5e61/'
PARTS = {
    'body_shell': ['FMA7163'],
    'lung_right': ['FMA7333', 'FMA7337', 'FMA7383'],
    'lung_left': ['FMA7370', 'FMA7371'],
    'heart': ['FMA7274'],
    'liver': ['FMA7197'],
    'stomach': ['FMA7148'],
    'brain': ['FMA61830', 'FMA72975', 'FMA72976', 'FMA67944', 'FMA67943', 'FMA62004'],
    'airway': ['FMA7394', 'FMA7409'],
    'esophagus': ['FMA7131'],
    'small_intestine': ['FMA7206', 'FMA7207', 'FMA7208'],
    'large_intestine': ['FMA14543nsn', 'FMA14544'],
    'kidney_left': ['FMA7205'],
    'kidney_right': ['FMA7204'],
    'bladder': ['FMA15900'],
    'pancreas': ['FMA7198nsn'],
    'gallbladder': ['FMA7202'],
    'muscle_deltoid_right': ['FMA34680', 'FMA34682', 'FMA34684'],
    'muscle_deltoid_left': ['FMA34681', 'FMA34683', 'FMA34685'],
    'muscle_pectoralis_right': ['FMA34690', 'FMA79979', 'FMA45874'],
    'muscle_pectoralis_left': ['FMA34691', 'FMA79980', 'FMA45875'],
    'muscle_biceps_right': ['FMA37684', 'FMA37686'],
    'muscle_biceps_left': ['FMA37685', 'FMA37687'],
    'muscle_triceps_right': ['FMA37695', 'FMA37697', 'FMA37699'],
    'muscle_triceps_left': ['FMA37696', 'FMA37698', 'FMA37700'],
    'muscle_abs_right': ['FMA13377'],
    'muscle_abs_left': ['FMA13378'],
    'muscle_oblique_right': ['FMA13336'],
    'muscle_oblique_left': ['FMA13337'],
    'muscle_trapezius_right': ['FMA33581', 'FMA33584', 'FMA33586'],
    'muscle_trapezius_left': ['FMA33583', 'FMA33585', 'FMA33587'],
    'muscle_latissimus_right': ['FMA13358'],
    'muscle_latissimus_left': ['FMA13359'],
    'muscle_gluteus_right': ['FMA22328'],
    'muscle_gluteus_left': ['FMA22329'],
    'muscle_rectus_femoris_right': ['FMA38928'],
    'muscle_rectus_femoris_left': ['FMA38929'],
    'muscle_vastus_lateralis_right': ['FMA38930'],
    'muscle_vastus_lateralis_left': ['FMA38931'],
    'muscle_biceps_femoris_right': ['FMA45888', 'FMA45891'],
    'muscle_biceps_femoris_left': ['FMA45889', 'FMA45892'],
    'muscle_gastrocnemius_right': ['FMA45957', 'FMA45960'],
    'muscle_gastrocnemius_left': ['FMA45958', 'FMA45961'],
    'muscle_tibialis_right': ['FMA22544'],
    'muscle_tibialis_left': ['FMA22545'],
    # Explicit bone roots avoid soft tissues included in source skeleton composites.
    'bone_skull': ['FMA52735', 'FMA52734', 'FMA52736', 'FMA52740', 'FMA9710', 'FMA52738', 'FMA52739', 'FMA52788', 'FMA52789', 'FMA52892', 'FMA52893', 'FMA53645', 'FMA53646', 'FMA53647', 'FMA53648', 'FMA53649', 'FMA53650', 'FMA53655', 'FMA53656', 'FMA54737', 'FMA54738'],
    'bone_mandible': ['FMA52748'],
    'bone_spine_cervical': ['FMA12519', 'FMA12520', 'FMA12521', 'FMA12522', 'FMA12523', 'FMA12524', 'FMA12525'],
    'bone_spine_thoracic': ['FMA9165', 'FMA9187', 'FMA9209', 'FMA9248', 'FMA9922', 'FMA9945', 'FMA9968', 'FMA9991', 'FMA10014', 'FMA10037', 'FMA10059', 'FMA10081'],
    'bone_spine_lumbar': ['FMA13072', 'FMA13073', 'FMA13074', 'FMA13075', 'FMA13076'],
    'bone_sacrum': ['FMA16202'],
    'bone_sternum': ['FMA7486', 'FMA7487', 'FMA7488'],
    'bone_ribs_right': ['FMA7857', 'FMA7882', 'FMA7909', 'FMA7957', 'FMA8066', 'FMA8175', 'FMA8229', 'FMA8283', 'FMA8364', 'FMA8445', 'FMA8531', 'FMA8533'],
    'bone_ribs_left': ['FMA7987', 'FMA8012', 'FMA8039', 'FMA8148', 'FMA8093', 'FMA8202', 'FMA8256', 'FMA8310', 'FMA8391', 'FMA8472', 'FMA8532', 'FMA8534'],
    'bone_clavicle_right': ['FMA13322'],
    'bone_clavicle_left': ['FMA13323'],
    'bone_scapula_right': ['FMA13395'],
    'bone_scapula_left': ['FMA13396'],
    'bone_humerus_right': ['FMA23130'],
    'bone_humerus_left': ['FMA23131'],
    'bone_radius_right': ['FMA23464'],
    'bone_radius_left': ['FMA23465'],
    'bone_ulna_right': ['FMA23467'],
    'bone_ulna_left': ['FMA23468'],
    'bone_hip_right': ['FMA16586'],
    'bone_hip_left': ['FMA16587'],
    'bone_femur_right': ['FMA24474'],
    'bone_femur_left': ['FMA24475'],
    'bone_patella_right': ['FMA24486'],
    'bone_patella_left': ['FMA24487'],
    'bone_tibia_right': ['FMA24477'],
    'bone_tibia_left': ['FMA24478'],
    'bone_fibula_right': ['FMA24480'],
    'bone_fibula_left': ['FMA24481'],
    'bone_hand_right': ['FMA23725', 'FMA24435', 'FMA24437', 'FMA24439', 'FMA24441', 'FMA24443', 'FMA24446', 'FMA24448', 'FMA24450', 'FMA24451', 'FMA24452', 'FMA24453', 'FMA24454', 'FMA24455', 'FMA24456', 'FMA24457', 'FMA24458', 'FMA24459', 'FMA24460', 'FMA24461', 'FMA24462', 'FMA24463', 'FMA24464', 'FMA24466', 'FMA24468', 'FMA24470', 'FMA24472'],
    'bone_hand_left': ['FMA23938', 'FMA23940', 'FMA23942', 'FMA23944', 'FMA23951', 'FMA23953', 'FMA23955', 'FMA23957', 'FMA23959', 'FMA24436', 'FMA24438', 'FMA24440', 'FMA24442', 'FMA24444', 'FMA24445', 'FMA24447', 'FMA24449', 'FMA24465', 'FMA24467', 'FMA24469', 'FMA24471', 'FMA24473', 'FMA65470', 'FMA66791', 'FMA71908', 'FMA71915', 'FMA71916'],
    'bone_foot_right': ['FMA230986', 'FMA24482', 'FMA24497', 'FMA24500', 'FMA24507', 'FMA24509', 'FMA24511', 'FMA24513', 'FMA24515', 'FMA24521', 'FMA24523', 'FMA24525', 'FMA24528', 'FMA32634', 'FMA32636', 'FMA32638', 'FMA32640', 'FMA32642', 'FMA32644', 'FMA32646', 'FMA32650', 'FMA32652', 'FMA32654', 'FMA32656', 'FMA32658', 'FMA43253'],
    'bone_foot_left': ['FMA230988', 'FMA24483', 'FMA24498', 'FMA24501', 'FMA24508', 'FMA24510', 'FMA24512', 'FMA24514', 'FMA24516', 'FMA24522', 'FMA24524', 'FMA24526', 'FMA24529', 'FMA32635', 'FMA32637', 'FMA32639', 'FMA32641', 'FMA32643', 'FMA32645', 'FMA32647', 'FMA32651', 'FMA32653', 'FMA32655', 'FMA32657', 'FMA32659', 'FMA43254'],
}
cache = ROOT / '.research' / 'anatomy_raw'
cache.mkdir(parents=True, exist_ok=True)
output = ROOT / 'assets' / 'viewer'
previous = trimesh.load(output / 'anatomy.glb') if (output / 'anatomy.glb').exists() else None
previous_manifest = json.loads((output / 'anatomy-manifest.json').read_text()) if previous else {}
tree = json.load(urllib.request.urlopen('https://api.github.com/repos/Kevin-Mattheus-Moerman/BodyParts3D/git/trees/f0eeb6e843380cfe6b83797cf8c3e1af74de5e61?recursive=1'))
available = {Path(item['path']).stem for item in tree['tree'] if item['path'].endswith('.stl')}
composites = {}
for line in urllib.request.urlopen(BASE + 'assets/BodyParts3D_data/composite_parts.txt').read().decode().splitlines():
    fields = line.split('\t')
    if len(fields) >= 4:
        composites.setdefault(fields[0], set()).add(fields[2])


def resolve(part, visited=None):
    visited = set() if visited is None else visited
    if part in visited:
        return set()
    visited.add(part)
    if part in available:
        return {part}
    children = composites.get(part, set())
    if not children:
        raise ValueError(f'No source geometry for {part}')
    return set().union(*(resolve(child, visited) for child in children))


def download(part):
    path = cache / f'{part}.stl'
    if not path.exists():
        urllib.request.urlretrieve(BASE + f'assets/BodyParts3D_data/stl/{part}.stl', path)
    return path


scene = trimesh.Scene()
manifest = {}
for name, roots in PARTS.items():
    ids = sorted(set().union(*(resolve(part) for part in roots)))
    target = 24000 if name in ['body_shell', 'brain', 'bone_skull'] else 8000
    old = previous_manifest.get(name, {})
    if previous is not None and sorted(old.get('parts', [])) == ids and name in previous.geometry:
        scene.add_geometry(previous.geometry[name], node_name=name, geom_name=name)
        manifest[name] = old
        print(name, 'reused existing reduced mesh', flush=True)
        continue
    with ThreadPoolExecutor(max_workers=6) as pool:
        paths = list(pool.map(download, ids))
    mesh = trimesh.util.concatenate([trimesh.load_mesh(path) for path in paths])
    if len(mesh.faces) > target:
        mesh = mesh.simplify_quadric_decimation(face_count=target)
    # BodyParts3D uses Z-up millimetres. Preserve shared anatomical coordinates.
    mesh.vertices = mesh.vertices[:, [0, 2, 1]] / 1000
    mesh.vertices[:, 2] *= -1
    scene.add_geometry(mesh, node_name=name, geom_name=name)
    manifest[name] = {'parts': ids, 'triangles': len(mesh.faces), 'bounds': mesh.bounds.tolist()}
    print(name, manifest[name], flush=True)
blob = scene.export(file_type='glb')
(output / 'anatomy.glb').write_bytes(blob)
(output / 'anatomy-data.js').write_text('window.ANATOMY_GLB = "' + base64.b64encode(blob).decode() + '";\n')
(output / 'anatomy-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
urllib.request.urlretrieve(BASE + 'LICENSE_content', output / 'BODY_PARTS_LICENSE.txt')
print('GLB bytes:', len(blob))
