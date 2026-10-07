"""Run with python3 tools/check_asset_licenses.py (standard library only)."""
import ast
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / '.research' / 'bodyparts3d-4.0-candidate'
BUNDLED = ROOT / 'assets' / 'viewer'
provenance = json.loads((ASSETS / 'anatomy-provenance.json').read_text())
assert provenance['license'] == 'CC-BY-4.0'
assert provenance['release'] == '4.0'
assert provenance['license_updated'] == '2025-02-27'

script = ast.parse((ROOT / 'tools' / 'prepare_official_anatomy.py').read_text())
constants = {node.targets[0].id: ast.literal_eval(node.value)
             for node in script.body if isinstance(node, ast.Assign)
             and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id in {'BASE', 'SOURCES', 'PARTS'}}
expected_sources = [{'url': constants['BASE'] + name, 'sha256': digest}
                    for name, digest in constants['SOURCES'].items()]
assert provenance['sources'] == expected_sources
assert constants['BASE'] == 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
assert set(provenance['artifacts']) == {'anatomy.glb', 'anatomy-data.js', 'anatomy-manifest.json'}
for name, digest in provenance['artifacts'].items():
    assert hashlib.sha256((ASSETS / name).read_bytes()).hexdigest() == digest, name

embedded = (ASSETS / 'anatomy-data.js').read_text()
assert embedded.startswith('window.ANATOMY_GLB = "') and embedded.endswith('";\n')
assert base64.b64decode(embedded.split('"')[1], validate=True) == (ASSETS / 'anatomy.glb').read_bytes()
manifest = json.loads((ASSETS / 'anatomy-manifest.json').read_text())
assert set(manifest) == set(constants['PARTS']) and len(manifest) == 16
for name, region in manifest.items():
    tree, concepts = constants['PARTS'][name]
    assert region['tree'] == tree and region['concepts'] == concepts, name
    assert region['parts'] and all(part.startswith('FJ') for part in region['parts']), name
    assert len(region['parts']) == len(set(region['parts'])), name
    assert region['triangles'] > 0, name

credit = 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.'
for name in ['CREDITS.txt', 'BODY_PARTS_LICENSE.txt']:
    text = (ASSETS / name).read_text()
    assert credit in text and 'https://creativecommons.org/licenses/by/4.0/' in text, name
assert 'Modifications:' in (ASSETS / 'CREDITS.txt').read_text()
assert 'MIT License' in (BUNDLED / 'THREE_LICENSE.txt').read_text()
pubspec = (ROOT / 'pubspec.yaml').read_text()
for name in ['CREDITS.txt', 'BODY_PARTS_LICENSE.txt', 'THREE_LICENSE.txt',
             'anatomy-manifest.json', 'anatomy-data.js']:
    assert f'assets/viewer/{name}' in pubspec, name

folder = ROOT / 'docs' / 'licensing' / 'bodyparts3d'
evidence = json.loads((folder / 'sources.json').read_text())
assert {record['file'] for record in evidence['sources']} == {
    'license.html', 'update.html', 'download.html', 'README_e.html', 'CC-BY-4.0.html'}
for record in evidence['sources']:
    assert hashlib.sha256((folder / record['file']).read_bytes()).hexdigest() == record['sha256'], record['file']
for name in ['AGENTS.md', 'INTEGRATION.md']:
    assert (ROOT / name).is_file(), name
assert 'CC BY-SA 2.1 Japan' in (BUNDLED / 'CREDITS.txt').read_text(), 'Revisit pending migration status'
print('PASS: staged candidate pins/hashes/base64, 16 regions, notices and official evidence; visual approval still pending')
