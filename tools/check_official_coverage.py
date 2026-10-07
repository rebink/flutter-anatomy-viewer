"""Fail closed if the official pinned sources cannot cover the current viewer IDs.

Run after prepare_official_anatomy.py. This checks concept/element coverage only,
not geometry quality, licensing clearance, or permission to promote the candidate.
No legacy mesh data is read or reused.
"""
import ast
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def constants(path):
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {'PARTS', 'SOURCES'}
    }


def main():
    official = constants(ROOT / 'tools/prepare_official_anatomy.py')
    legacy = constants(ROOT / 'tools/prepare_anatomy.py')['PARTS']
    cache = ROOT / '.research/bodyparts3d-4.0-official'
    for name, digest in official['SOURCES'].items():
        if hashlib.sha256((cache / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Source checksum mismatch: {name}')

    mappings = {}
    for tree in ('isa', 'partof'):
        mapping = {}
        with (cache / f'{tree}_element_parts.txt').open() as source:
            rows = csv.reader(source, delimiter='\t')
            next(rows)
            for concept, label, element in rows:
                entry = mapping.setdefault(concept, {'label': label, 'elements': set()})
                entry['elements'].add(element)
        mappings[tree] = mapping
    with zipfile.ZipFile(cache / 'isa_BP3D_4.0_obj_99.zip') as archive:
        members = {Path(name).stem for name in archive.namelist() if name.endswith('.obj')}

    report = {}
    for name, legacy_concepts in legacy.items():
        tree, concepts = official['PARTS'].get(name, ('isa', legacy_concepts))
        mapping = mappings[tree]
        missing = [concept for concept in concepts if concept not in mapping]
        elements = sorted(set().union(*(mapping[c]['elements'] for c in concepts if c in mapping)))
        report[name] = {
            'tree': tree, 'concepts': concepts,
            'labels': [mapping[c]['label'] for c in concepts if c in mapping],
            'elements': elements, 'missing_concepts': missing,
            'missing_elements': sorted(set(elements) - members),
        }
    failed = [name for name, item in report.items()
              if item['missing_concepts'] or item['missing_elements'] or not item['elements']]
    print(json.dumps({'regions': report, 'unresolved_regions': failed,
                      'geometry_approval': 'not assessed'}, indent=2))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
