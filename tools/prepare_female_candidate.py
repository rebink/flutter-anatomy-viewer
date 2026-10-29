"""Build a source-labeled female illustration; NEVER modifies bundled app assets.

HRA proportions are preserved. Missing regions use fresh official BodyParts3D
meshes, except four unavailable muscles explicitly retained under their legacy
license. This is not a fully female-derived atlas or an approved release.
"""

import argparse
import ast
import base64
import csv
import hashlib
import io
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from prepare_official_anatomy import BASE, SOURCES
from trimesh.visual.color import ColorVisuals

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".research/female-anatomy/3d-vh-f-united.glb"
LEGACY = ROOT / "assets/viewer"
OUTPUT = ROOT / ".research/female-open-candidate"
HRA_HASH = "95f0c3d2f918582608692ca1139e8bdb18c147a16470e9ee9af8b276bd77c422"
HRA_URL = (
    "https://cdn.humanatlas.io/dvc/hra-kg/files/md5/5e/4aca68ceea6aa9b21aa9c333c54fec"
)
LEGACY_HASH = "643362925b4bcb9c79a6619ea54ec359739192663b5cbc787b981214804695bf"
OFFICIAL_FILES = ("isa_BP3D_4.0_obj_99.zip", "isa_element_parts.txt")
# Release 4.0 does not map these concepts. Never substitute a neighboring muscle.
LEGACY_REGIONS = {
    "muscle_abs_left",
    "muscle_abs_right",
    "muscle_latissimus_left",
    "muscle_latissimus_right",
}
HRA_NODES = {
    "body_shell": ["VH_F_skin"],
    "brain": ["Allen_brain"],
    "lung_left": ["VH_F_left_lungs_L"],
    "lung_right": ["VH_F_lungs_R"],
    "heart": ["VH_F_heart"],
    "liver": ["VH_F_liver"],
    "airway": ["VH_F_tracheobronchial_tree"],
    "pancreas": ["VH_F_pancreas"],
    "gallbladder": ["VH_F_gallbladder"],
    "small_intestine": ["VH_F_small_intestine"],
    "large_intestine": ["VH_F_colon"],
    "kidney_left": ["VH_F_left_kidney"],
    "kidney_right": ["VH_F_right_kidney"],
    "bladder": ["VH_F_urinary_bladder"],
    "breast_left": ["VH_F_mammary_gland_L"],
    "breast_right": ["VH_F_mammary_gland_R"],
    "uterus": ["VH_F_uterus"],
    "vagina": ["VH_F_vagina"],
    "ovary_left": ["VH_F_left_ovary"],
    "ovary_right": ["VH_F_right_ovary"],
    "fallopian_tube_left": ["VH_F_fallopian_tube_L"],
    "fallopian_tube_right": ["VH_F_fallopian_tube_R"],
    "muscle_rectus_femoris_left": ["VH_F_rectus_femoris_L"],
    "muscle_rectus_femoris_right": ["VH_F_rectus_femoris_R"],
    "bone_sacrum": ["VH_F_sacrum"],
    "bone_sternum": ["VH_F_sternum", "VH_F_manubrium"],
    "bone_spine_cervical": [f"VH_F_cervical_vertebra_{i}" for i in range(1, 8)],
    "bone_spine_thoracic": [f"VH_F_thoracic_vertebra_{i}" for i in range(1, 13)],
    "bone_spine_lumbar": [f"VH_F_lumbar_vertebra_{i}" for i in range(1, 7)],
}
for region in ["femur", "tibia", "fibula", "patella"]:
    for side, suffix in [("left", "L"), ("right", "R")]:
        HRA_NODES[f"bone_{region}_{side}"] = [f"VH_F_{region}_{suffix}"]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(path, expected):
    if digest(path) != expected:
        raise ValueError(
            f"Source changed; review provenance rather than repinning: {path}"
        )


def fetch(url, path, expected):
    if url not in [HRA_URL, *(BASE + name for name in OFFICIAL_FILES)]:
        raise ValueError("Only pinned official HTTPS source URLs are permitted")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".download")
        try:
            with (
                urllib.request.urlopen(url, timeout=120) as response,
                temporary.open("wb") as out,
            ):
                shutil.copyfileobj(response, out)
            verify(temporary, expected)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    verify(path, expected)
    return path


def selection_parts():
    # Read the established ID inventory without executing the legacy asset builder.
    script = ast.parse((ROOT / "tools/prepare_anatomy.py").read_text())
    return next(
        ast.literal_eval(node.value)
        for node in script.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "PARTS"
    )


def extract(scene: trimesh.Scene, roots: list[str]) -> trimesh.Trimesh:
    """Collect each descendant mesh once and preserve source world transforms."""
    selected = set()
    children = scene.graph.transforms.children
    stack = list(roots)
    while stack:
        node = stack.pop()
        if node in selected:
            continue
        if node not in scene.graph.nodes:
            raise ValueError(f"Missing source node: {node}")
        selected.add(node)
        stack.extend(children.get(node, []))
    meshes = []
    for node in sorted(selected):
        transform, geometry = scene.graph[node]
        if geometry is not None:
            mesh = scene.geometry[geometry].copy()
            if not isinstance(mesh, trimesh.Trimesh):
                raise ValueError(f"Non-triangle geometry: {node}")
            mesh.apply_transform(transform)
            meshes.append(mesh)
    if not meshes:
        raise ValueError(f"No geometry under {roots}")
    combined = trimesh.util.concatenate(meshes)
    assert isinstance(combined, trimesh.Trimesh)
    return combined


def adapt(mesh: trimesh.Trimesh, name: str) -> trimesh.Trimesh:
    """Illustrative registration only; not a female anatomical reconstruction."""
    points = mesh.vertices.copy()
    y = points[:, 1].copy()
    # ponytail: coarse landmark warp; replace with reviewed rig registration for anatomical fidelity.
    points[:, 1] = np.interp(
        y, [-0.02, 0.41, 0.85, 1.35, 1.65], [-0.80, -0.38, 0.045, 0.555, 0.865]
    )
    points[:, 2] -= 0.155
    points[:, 0] *= 1.15
    arm = (
        any(
            part in name
            for part in [
                "deltoid",
                "biceps_",
                "triceps_",
                "humerus",
                "radius",
                "ulna",
                "hand",
            ]
        )
        and "femoris" not in name
    )
    if arm:
        side = 1 if name.endswith("_left") else -1
        shift = np.interp(
            y, [0.65, 0.82, 1.05, 1.35, 1.5], [0.105, 0.105, 0.055, 0.0, 0.0]
        )
        points[:, 0] += side * shift
        points[:, 1] += np.interp(
            y, [0.65, 0.82, 1.05, 1.35], [0.045, 0.045, 0.025, 0.0]
        )
    elif any(
        part in name
        for part in [
            "gluteus",
            "vastus",
            "biceps_femoris",
            "gastrocnemius",
            "tibialis",
            "bone_foot",
        ]
    ):
        points[:, 0] += 0.02 if name.endswith("_left") else -0.02
    mesh.vertices = points
    return mesh


def verify_official_evidence():
    folder = ROOT / "docs/licensing/bodyparts3d"
    index = folder / "sources.json"
    records = json.loads(index.read_text())["sources"]
    required = {
        "license.html",
        "update.html",
        "download.html",
        "README_e.html",
        "CC-BY-4.0.html",
    }
    if {record["file"] for record in records} != required:
        raise ValueError("Official license evidence inventory is incomplete")
    for record in records:
        verify(folder / record["file"], record["sha256"])
    return {
        "sources.json": digest(index),
        **{record["file"]: record["sha256"] for record in records},
    }


def prepare_output_directory():
    if OUTPUT.resolve() != ROOT / ".research/female-open-candidate":
        raise ValueError("Refusing redirected candidate output directory")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        if path.is_symlink() or (path.is_file() and path.stat().st_nlink > 1):
            raise ValueError(f"Refusing linked candidate output: {path}")
    # No preview may accept a partially written or rejected rebuild.
    (OUTPUT / "anatomy-provenance.json").unlink(missing_ok=True)


def write_validated_provenance(provenance):
    pending = OUTPUT / "anatomy-provenance.pending.json"
    try:
        pending.write_text(json.dumps(provenance, indent=2) + "\n")
        check(pending)
        pending.replace(OUTPUT / "anatomy-provenance.json")
    finally:
        pending.unlink(missing_ok=True)


def check(provenance_file=None):
    evidence_hashes = verify_official_evidence()
    parts = selection_parts()
    required = set(parts) | set(HRA_NODES)
    manifest = json.loads((OUTPUT / "anatomy-manifest.json").read_text())
    provenance = json.loads(
        (provenance_file or OUTPUT / "anatomy-provenance.json").read_text()
    )
    assert provenance["official_evidence_sha256"] == evidence_hashes
    assert provenance["status"] == "illustrative-candidate-not-approved"
    assert provenance["anatomically_validated"] is False
    assert provenance["generator_sha256"] == digest(Path(__file__)), (
        "Rebuild after generator changes"
    )
    assert provenance["input_sha256"]["hra-female"] == HRA_HASH
    assert provenance["input_sha256"]["legacy-bundled-glb"] == LEGACY_HASH
    assert provenance["selection_inventory_sha256"] == digest(
        ROOT / "tools/prepare_anatomy.py"
    )
    assert provenance["hra_source_url"] == HRA_URL
    assert provenance["official_sources"] == [
        {"url": BASE + name, "sha256": SOURCES[name]} for name in OFFICIAL_FILES
    ]
    assert set(manifest) == required, "Candidate dropped or invented selection IDs"
    expected_files = {
        "anatomy.glb",
        "anatomy-data.js",
        "anatomy-manifest.json",
        "CREDITS.txt",
        "HRA_METADATA.yaml",
        "BODY_PARTS_LICENSE.txt",
        "LEGACY_BODY_PARTS_LICENSE.txt",
        "THREE_LICENSE.txt",
    }
    assert set(provenance["output_sha256"]) == expected_files
    for name, expected in provenance["output_sha256"].items():
        verify(OUTPUT / name, expected)
    embedded = (OUTPUT / "anatomy-data.js").read_text()
    assert embedded.startswith('window.ANATOMY_GLB = "') and embedded.endswith('";\n')
    assert (
        base64.b64decode(embedded.split('"')[1], validate=True)
        == (OUTPUT / "anatomy.glb").read_bytes()
    )
    scene = trimesh.load_scene(OUTPUT / "anatomy.glb", process=False)
    assert set(scene.geometry) == required, "GLB and manifest disagree"
    for name, mesh in scene.geometry.items():
        assert isinstance(mesh, trimesh.Trimesh), name
        region = manifest[name]
        expected_source = (
            "hra-female"
            if name in HRA_NODES
            else "adapted-legacy"
            if name in LEGACY_REGIONS
            else "adapted-official"
        )
        assert region["source"] == expected_source, name
        assert region["license"] == (
            "CC BY-SA 2.1 Japan" if name in LEGACY_REGIONS else "CC BY 4.0"
        ), name
        assert region["anatomically_validated"] is False, name
        assert region["source_nodes"] == HRA_NODES.get(name, []), name
        assert region["source_parts"] or name in HRA_NODES, name
        assert len(mesh.faces) > 0 and np.isfinite(mesh.vertices).all(), name
        assert len(mesh.faces) == region["triangles"], name
        assert np.allclose(mesh.bounds, region["bounds"], atol=1e-6), name
        assert np.all(np.ptp(mesh.bounds, axis=0) > 0), name
        assert (
            (0.90 if name == "body_shell" else 0.50)
            <= mesh.area / region["source_area"]
            <= 1.15
        ), name
        if name in HRA_NODES:
            assert np.allclose(mesh.bounds, region["source_bounds"], atol=0.006), name
            assert (
                region["registration"] == "source world coordinates; no shape warp"
            ), name
        if name.endswith("_left"):
            assert mesh.bounds[:, 0].mean() > 0, name
        if name.endswith("_right"):
            assert mesh.bounds[:, 0].mean() < 0, name
    assert (OUTPUT / "LEGACY_BODY_PARTS_LICENSE.txt").read_bytes() == (
        LEGACY / "BODY_PARTS_LICENSE.txt"
    ).read_bytes()
    credits = (OUTPUT / "CREDITS.txt").read_text()
    for text in [
        "CC BY 4.0",
        "CC BY-SA 2.1 Japan",
        "not clinically validated",
        "Courtesy of the U.S. National Library of Medicine",
    ]:
        assert text in credits, text
    print(
        f"PASS: {len(required)} regions, sources/licenses, geometry, source proportions, embedded GLB and hashes; NOT anatomical approval"
    )


def build():
    evidence_hashes = verify_official_evidence()
    fetch(HRA_URL, SOURCE, HRA_HASH)
    verify(LEGACY / "anatomy.glb", LEGACY_HASH)
    cache = ROOT / ".research/bodyparts3d-4.0-official"
    paths = {
        name: fetch(BASE + name, cache / name, SOURCES[name]) for name in OFFICIAL_FILES
    }
    evidence = ROOT / "docs/licensing/hra-female"
    for record in json.loads((evidence / "sources.json").read_text()):
        if record["file"] != SOURCE.name:
            verify(evidence / record["file"], record["sha256"])
    parts = selection_parts()
    mapping = {}
    with paths["isa_element_parts.txt"].open() as stream:
        rows = csv.reader(stream, delimiter="\t")
        next(rows)
        for concept, _label, element in rows:
            mapping.setdefault(concept, set()).add(element)
    source = trimesh.load_scene(SOURCE, process=False)
    legacy = trimesh.load_scene(LEGACY / "anatomy.glb", process=False)
    baseline = json.loads((LEGACY / "anatomy-manifest.json").read_text())
    result = trimesh.Scene()
    manifest = {}
    with zipfile.ZipFile(paths["isa_BP3D_4.0_obj_99.zip"]) as archive:
        members = {
            Path(name).stem: name
            for name in archive.namelist()
            if name.endswith(".obj")
        }
        for name in list(parts) + [key for key in HRA_NODES if key not in parts]:
            source_parts = []
            if name in HRA_NODES:
                mesh = extract(source, HRA_NODES[name])
                origin = "hra-female"
            elif name in LEGACY_REGIONS:
                mesh = adapt(extract(legacy, [name]), name)
                source_parts = baseline[name]["parts"]
                origin = "adapted-legacy"
            else:
                source_parts = sorted(
                    set().union(*(mapping[concept] for concept in parts[name]))
                )
                meshes = [
                    trimesh.load_mesh(
                        io.BytesIO(archive.read(members[part])), file_type="obj"
                    )
                    for part in source_parts
                ]
                mesh = trimesh.util.concatenate(meshes)
                assert isinstance(mesh, trimesh.Trimesh)
                mesh.vertices = mesh.vertices[:, [0, 2, 1]] / 1000
                mesh.vertices[:, 2] *= -1
                mesh = adapt(mesh, name)
                origin = "adapted-official"
            source_area, source_bounds = float(mesh.area), mesh.bounds.tolist()
            # Welding HRA seam vertices prevents reduction from deleting isolated triangles.
            mesh.merge_vertices(merge_tex=True, merge_norm=True)
            target = 24000 if name in ["body_shell", "brain", "bone_skull"] else 8000
            if len(mesh.faces) > target:
                mesh = mesh.simplify_quadric_decimation(face_count=target)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            mesh.visual = ColorVisuals(mesh=mesh)
            if not np.isfinite(mesh.vertices).all() or not len(mesh.faces):
                raise ValueError(f"Invalid generated mesh: {name}")
            result.add_geometry(mesh, node_name=name, geom_name=name)
            manifest[name] = {
                "source": origin,
                "license": "CC BY-SA 2.1 Japan"
                if name in LEGACY_REGIONS
                else "CC BY 4.0",
                "source_nodes": HRA_NODES.get(name, []),
                "source_parts": source_parts,
                "source_concepts": [] if name in HRA_NODES else parts[name],
                "registration": "source world coordinates; no shape warp"
                if name in HRA_NODES
                else "illustrative landmark warp; not reviewed anatomical registration",
                "modifications": "combined descendants/elements, welded seams, simplified, converted to GLB; no cosmetic slimming",
                "anatomically_validated": False,
                "source_area": source_area,
                "source_bounds": source_bounds,
                "triangles": len(mesh.faces),
                "bounds": mesh.bounds.tolist(),
            }
            print(name, origin, len(mesh.faces), flush=True)
    prepare_output_directory()
    blob = result.export(file_type="glb")
    assert isinstance(blob, bytes)
    (OUTPUT / "anatomy.glb").write_bytes(blob)
    (OUTPUT / "anatomy-data.js").write_text(
        'window.ANATOMY_GLB = "' + base64.b64encode(blob).decode() + '";\n'
    )
    (OUTPUT / "anatomy-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copyfile(
        LEGACY / "BODY_PARTS_LICENSE.txt", OUTPUT / "LEGACY_BODY_PARTS_LICENSE.txt"
    )
    shutil.copyfile(LEGACY / "THREE_LICENSE.txt", OUTPUT / "THREE_LICENSE.txt")
    shutil.copyfile(evidence / "metadata.yaml", OUTPUT / "HRA_METADATA.yaml")
    shutil.copyfile(
        ROOT / "docs/licensing/bodyparts3d/CANDIDATE_LICENSE.txt",
        OUTPUT / "BODY_PARTS_LICENSE.txt",
    )
    (OUTPUT / "CREDITS.txt").write_text(
        "ILLUSTRATIVE FEMALE COMPOSITE - NOT APPROVED FOR RELEASE\n"
        "Generated by tools/prepare_female_candidate.py; not clinically validated.\n"
        "37 regions from the HRA female reference set; 44 adapted official\n"
        "BodyParts3D regions; four adapted legacy muscles. Dataset membership\n"
        "does not establish donor sex for every component (e.g. Allen brain).\n"
        "This is not a complete female-source atlas or patient reconstruction.\n\n"
        "HRA: Browne, Kristen, and Heidi Schlehlein. 2026.\n"
        "3D Reference Organ Set for Female v1.10. HuBMAP Human Reference Atlas.\n"
        "https://doi.org/10.48539/HBM637.DWBM.744\n"
        "CC BY 4.0: https://creativecommons.org/licenses/by/4.0/\n"
        "Courtesy of the U.S. National Library of Medicine.\n"
        "Metadata/bibliography retained in HRA_METADATA.yaml.\n"
        "Modifications: selection, combination, welded seams, reduction and GLB\n"
        "conversion. Source world transforms preserved; no abdomen flattening\n"
        "or athletic-proportion warp. Reduction is not anatomical validation.\n\n"
        "OFFICIAL BODYPARTS3D RELEASE 4.0\n"
        "BodyParts3D, Copyright The Database Center for Life Science licensed\n"
        "under CC Attribution 4.0 International (CC BY 4.0).\n"
        "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html\n"
        "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html\n"
        "https://creativecommons.org/licenses/by/4.0/\n"
        "Fresh official OBJ elements, not reused legacy geometry. Combined,\n"
        "converted axes/units, coarsely registered to the HRA pose and reduced.\n"
        "Male-derived adaptations, not measured female muscles/bones. The old\n"
        "OBJ header license differs from the dated official grant; evidence is\n"
        "in docs/licensing/bodyparts3d/. See BODY_PARTS_LICENSE.txt.\n\n"
        "LEGACY EXCEPTIONS: bilateral rectus abdominis and latissimus dorsi\n"
        "are absent from the official 4.0 concept mappings. These four regions\n"
        "retain CC BY-SA 2.1 Japan and its share-alike terms. No relabeling.\n"
        "https://creativecommons.org/licenses/by-sa/2.1/jp/\n"
        "Source: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D/tree/"
        "f0eeb6e843380cfe6b83797cf8c3e1af74de5e61\n"
        "BodyParts3D, Copyright The Database Center for Life Science.\n"
        "Modifications: existing reduction plus illustrative landmark warp.\n"
        "See LEGACY_BODY_PARTS_LICENSE.txt. Mixed-source distribution review\n"
        "is unresolved; there is NO blanket MIT or CC BY-only model license.\n\n"
        "All regions: illustrative runtime materials. No endorsement implied.\n"
        "Per-region provenance: anatomy-manifest.json. Anatomical registration,\n"
        "source approval and publication gates remain. Keep attribution visible\n"
        "even when loading fails. Three.js r170: MIT; see THREE_LICENSE.txt.\n"
    )
    outputs = [
        "anatomy.glb",
        "anatomy-data.js",
        "anatomy-manifest.json",
        "CREDITS.txt",
        "HRA_METADATA.yaml",
        "BODY_PARTS_LICENSE.txt",
        "LEGACY_BODY_PARTS_LICENSE.txt",
        "THREE_LICENSE.txt",
    ]
    provenance = {
        "status": "illustrative-candidate-not-approved",
        "anatomically_validated": False,
        "input_sha256": {"hra-female": HRA_HASH, "legacy-bundled-glb": LEGACY_HASH},
        "official_sources": [
            {"url": BASE + name, "sha256": SOURCES[name]} for name in OFFICIAL_FILES
        ],
        "hra_source_url": HRA_URL,
        "official_evidence_sha256": evidence_hashes,
        "generator_sha256": digest(Path(__file__)),
        "selection_inventory_sha256": digest(ROOT / "tools/prepare_anatomy.py"),
        "output_sha256": {name: digest(OUTPUT / name) for name in outputs},
    }
    write_validated_provenance(provenance)
    print("Candidate only:", OUTPUT, "bytes:", len(blob))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate existing candidate without rebuilding",
    )
    args = parser.parse_args()
    check() if args.check else build()
