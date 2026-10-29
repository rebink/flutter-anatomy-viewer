// Local-only UI comparison. Reuses the bundled renderer; never rewrites app assets.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..');
const ASSETS = path.join(ROOT, 'assets/viewer');
const CANDIDATE = path.join(ROOT, '.research/female-open-candidate');

function femaleData() {
  const bytes = fs.readFileSync(path.join(CANDIDATE, 'anatomy.glb'));
  const provenance = JSON.parse(fs.readFileSync(path.join(CANDIDATE, 'anatomy-provenance.json'), 'utf8'));
  assert.equal(provenance.status, 'illustrative-candidate-not-approved');
  assert.equal(provenance.anatomically_validated, false);
  assert.deepEqual(Object.keys(provenance.official_evidence_sha256).sort(), ['sources.json', 'license.html', 'update.html', 'download.html', 'README_e.html', 'CC-BY-4.0.html'].sort());
  for (const [name, hash] of Object.entries(provenance.official_evidence_sha256)) {
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, 'docs/licensing/bodyparts3d', name))).digest('hex'), hash, `Official license evidence changed: ${name}`);
  }
  const files = ['anatomy.glb', 'anatomy-data.js', 'anatomy-manifest.json', 'CREDITS.txt', 'HRA_METADATA.yaml', 'BODY_PARTS_LICENSE.txt', 'LEGACY_BODY_PARTS_LICENSE.txt', 'THREE_LICENSE.txt'];
  assert.deepEqual(Object.keys(provenance.output_sha256).sort(), files.sort());
  for (const name of files) {
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(CANDIDATE, name))).digest('hex'), provenance.output_sha256[name], `Candidate hash mismatch: ${name}; rebuild/review first`);
  }
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, 'tools/prepare_female_candidate.py'))).digest('hex'), provenance.generator_sha256, 'Generator changed; rebuild candidate');
  assert.equal(bytes.readUInt32LE(0), 0x46546c67);
  assert.equal(bytes.readUInt32LE(4), 2);
  assert.equal(bytes.readUInt32LE(8), bytes.length);
  const length = bytes.readUInt32LE(12);
  assert.equal(bytes.readUInt32LE(16), 0x4e4f534a);
  const gltf = JSON.parse(bytes.subarray(20, 20 + length).toString());
  // Presentation-only translation into the existing renderer's Y-up camera frame.
  // No shape scaling or anatomical registration is implied by this offset.
  for (const scene of gltf.scenes) {
    const index = gltf.nodes.length;
    gltf.nodes.push({ name: 'candidate_camera_frame', children: scene.nodes, translation: [0, 0.785, 0.155] });
    scene.nodes = [index];
  }
  const json = Buffer.from(JSON.stringify(gltf));
  const padded = Buffer.alloc(Math.ceil(json.length / 4) * 4, 0x20); json.copy(padded);
  const binary = bytes.subarray(20 + length);
  const header = Buffer.alloc(20);
  header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4);
  header.writeUInt32LE(20 + padded.length + binary.length, 8);
  header.writeUInt32LE(padded.length, 12); header.writeUInt32LE(0x4e4f534a, 16);
  return `window.ANATOMY_GLB = ${JSON.stringify(Buffer.concat([header, padded, binary]).toString('base64'))};`;
}

function catalog() {
  const dart = fs.readFileSync(path.join(ROOT, 'lib/main.dart'), 'utf8');
  function names(constant) {
    // These are existing literal maps, not arbitrary Dart evaluation. Fail closed if changed.
    const block = dart.match(new RegExp(`const ${constant} = \\{([\\s\\S]*?)\\n\\};`));
    assert(block, `Missing literal map: ${constant}`);
    const result = Object.fromEntries([...block[1].matchAll(/'([^']+)': '([^']+)',/g)].map(match => [match[1], match[2]]));
    assert(Object.keys(result).length > 0, `Empty literal map: ${constant}`);
    return result;
  }
  const male = { body: names('organNames'), muscles: names('muscleNames'), bones: names('boneNames') };
  const female = { ...male, body: { ...male.body,
    breast_left: 'Left breast / mammary gland', breast_right: 'Right breast / mammary gland',
    uterus: 'Uterus & cervix', vagina: 'Vagina', ovary_left: 'Left ovary', ovary_right: 'Right ovary',
    fallopian_tube_left: 'Left fallopian tube', fallopian_tube_right: 'Right fallopian tube',
  } };
  const manifest = JSON.parse(fs.readFileSync(path.join(CANDIDATE, 'anatomy-manifest.json'), 'utf8'));
  assert.deepEqual(new Set(Object.values(female).flatMap(Object.keys)), new Set(Object.keys(manifest).filter(id => id !== 'body_shell')));
  const maleSources = Object.fromEntries(Object.values(male).flatMap(entries => Object.keys(entries)).map(id => [id, { source: 'legacy-male', license: 'CC BY-SA 2.1 Japan' }]));
  return { male, female, provenance: { male: maleSources, female: manifest } };
}

async function check(server) {
  const { chromium } = require('playwright');
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1000, height: 1100 }, reducedMotion: 'reduce' });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    const ready = () => page.waitForFunction(() => !document.querySelector('#reset').disabled);
    await ready();
    assert.equal(await page.locator('[data-structure]').count(), 23);
    assert.equal(await page.getByRole('button', { name: /Female/ }).getAttribute('aria-pressed'), 'true');
    await page.screenshot({ path: path.join(CANDIDATE, 'same-ui-female.png'), fullPage: true });
    for (let turn = 0; turn < 6; turn++) await page.getByRole('button', { name: 'Rotate right', exact: true }).click();
    await page.locator('.stage').screenshot({ path: path.join(CANDIDATE, 'same-ui-female-side.png') });
    await page.getByRole('button', { name: 'Reset body view', exact: true }).click();
    for (const label of ['Left breast / mammary gland', 'Right breast / mammary gland', 'Uterus & cervix', 'Left ovary', 'Right ovary', 'Left fallopian tube', 'Right fallopian tube', 'Vagina']) {
      await page.getByRole('button', { name: label, exact: true }).click();
      assert.equal(await page.locator('#selected').textContent(), label);
      assert.match(await page.locator('#source-detail').textContent(), /HRA female reference set.*CC BY 4\.0/);
    }
    await page.locator('.stage').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(CANDIDATE, 'same-ui-female-focus.png') });
    for (const [label, count] of [['Muscles', 28], ['Bones', 33]]) {
      await page.getByRole('button', { name: label, exact: true }).click();
      assert.equal(await page.locator('[data-structure]').count(), count);
      for (const button of await page.locator('[data-structure]').all()) {
        await button.click();
        assert.notEqual(await page.locator('#selected').textContent(), '');
        assert.match(await page.locator('#source-detail').textContent(), /not clinically validated/);
      }
      if (label === 'Muscles') {
        await page.locator('[data-structure="muscle_abs_left"]').click();
        assert.match(await page.locator('#source-detail').textContent(), /Legacy male-derived adaptation.*CC BY-SA 2\.1 Japan/);
        await page.locator('[data-structure="muscle_deltoid_left"]').click();
        assert.match(await page.locator('#source-detail').textContent(), /Official BodyParts3D adaptation.*CC BY 4\.0/);
      }
      await page.getByRole('button', { name: 'Reset body view', exact: true }).click();
      assert.equal(await page.locator('#source-detail').textContent(), '');
      assert.equal(await page.locator('#selected').textContent(), '');
      await page.screenshot({ path: path.join(CANDIDATE, `same-ui-${label.toLowerCase()}.png`), fullPage: true });
    }
    await page.getByRole('button', { name: 'Body Parts', exact: true }).click();
    await page.getByRole('button', { name: 'Uterus & cervix', exact: true }).click();
    await page.getByLabel('Organ opacity').evaluate(input => { input.value = '60'; input.dispatchEvent(new Event('input', { bubbles: true })); });
    assert((await page.locator('#opacity-label').textContent()).includes('60%'));
    assert.equal(await page.locator('[data-structure="uterus"]').getAttribute('aria-pressed'), 'true');
    for (const label of ['Rotate left', 'Rotate right', 'Zoom in', 'Zoom out']) await page.getByRole('button', { name: label, exact: true }).click();
    await page.getByRole('button', { name: 'Male', exact: true }).click(); await ready();
    assert.equal(await page.locator('[data-structure]').count(), 15);
    assert.equal(await page.locator('[data-structure="uterus"]').count(), 0);
    assert.equal(await page.locator('#candidate-note').isVisible(), false);
    assert.equal(await page.locator('#source-detail').textContent(), '');
    await page.screenshot({ path: path.join(CANDIDATE, 'same-ui-male.png'), fullPage: true });
    await page.getByRole('button', { name: /Female/ }).click(); await ready();
    assert.equal(await page.locator('[data-structure]').count(), 23);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole('button', { name: 'Reset body view', exact: true }).click();
    await page.evaluate(() => scrollTo(0, 0));
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({ path: path.join(CANDIDATE, 'same-ui-mobile.png'), fullPage: true });
    await page.getByRole('button', { name: 'Credits and licenses', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('#credits-text').textContent.includes('CC BY-SA 2.1 Japan'));
    assert((await page.locator('#credits-text').textContent()).includes('CC BY 4.0'));
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#credits-dialog').isVisible(), false);
    // Attribution must remain usable when model loading fails.
    await page.route('**/viewer/anatomy-data.js?*', route => route.abort());
    await page.getByRole('button', { name: /Female/ }).click();
    await page.waitForFunction(() => document.querySelector('#scene-status').textContent.includes('3D unavailable'));
    await page.getByRole('button', { name: 'Credits and licenses', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('#credits-text').textContent.includes('CC BY-SA 2.1 Japan'));
    await page.keyboard.press('Escape');
    await page.unroute('**/viewer/anatomy-data.js?*');
    await page.getByRole('button', { name: /Female/ }).click(); await ready();
    assert.equal(await page.locator('[data-structure]').count(), 23);
    assert.deepEqual(errors, []);
    console.log('PASS: shared renderer, all female lists, per-region provenance, focus/reset, three modes, opacity, camera controls, mobile layout, failure-independent credits and retry');
  } finally { await browser.close(); }
}

(async () => {
  const data = femaleData(); const names = JSON.stringify(catalog());
  const html = fs.readFileSync(path.join(__dirname, 'candidate-preview.html'));
  const viewer = fs.readFileSync(path.join(ASSETS, 'index.html'), 'utf8');
  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url, 'http://127.0.0.1');
      const female = url.searchParams.get('model') === 'female';
      res.setHeader('Cache-Control', 'no-store');
      function reply(type, body) { res.setHeader('Content-Type', type); res.end(body); }
      if (url.pathname === '/') return reply('text/html; charset=utf-8', html);
      if (url.pathname === '/catalog.json') return reply('application/json', names);
      if (url.pathname === '/viewer/index.html') {
        const generation = Number(url.searchParams.get('generation')) || 0;
        return reply('text/html; charset=utf-8', viewer.replace('<script src="anatomy-data.js"></script>', `<script src="/bridge.js?generation=${generation}"></script><script src="anatomy-data.js?model=${female ? 'female' : 'male'}"></script>`));
      }
      if (url.pathname === '/bridge.js') {
        const generation = Number(url.searchParams.get('generation')) || 0;
        return reply('text/javascript', `window.AnatomyBridge={postMessage(value){parent.postMessage({...JSON.parse(value),generation:${generation}},location.origin)}};`);
      }
      if (url.pathname === '/viewer/anatomy-data.js') return reply('text/javascript', female ? data : fs.readFileSync(path.join(ASSETS, 'anatomy-data.js')));
      if (url.pathname === '/viewer/viewer.js') return reply('text/javascript', fs.readFileSync(path.join(ASSETS, 'viewer.js')));
      if (['/credits/female.txt', '/credits/male.txt'].includes(url.pathname)) return reply('text/plain; charset=utf-8', fs.readFileSync(path.join(url.pathname.includes('female') ? CANDIDATE : ASSETS, 'CREDITS.txt')));
      res.writeHead(404); res.end('Not found');
    } catch (error) { console.error(error); res.writeHead(500); res.end('Preview unavailable'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  if (process.argv.includes('--check')) {
    try { await check(server); } finally { server.close(); }
  } else console.log(`Same-UI anatomy preview: http://127.0.0.1:${server.address().port}/`);
})().catch(error => { console.error(error); process.exitCode = 1; });
