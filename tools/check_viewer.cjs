const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 530 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => {
      window.messages = [];
      window.drawCount = 0;
      window.badAlphaDraws = 0;
      window.diffuseColors = new Set();
      for (const Context of [window.WebGLRenderingContext, window.WebGL2RenderingContext]) {
        const draw = Context.prototype.drawElements;
        const opaquePrograms = new WeakMap();
        Context.prototype.drawElements = function (...args) {
          window.drawCount++;
          const program = this.getParameter(this.CURRENT_PROGRAM);
          if (!opaquePrograms.has(program)) {
            opaquePrograms.set(program, this.getAttachedShaders(program).some(shader =>
              this.getShaderParameter(shader, this.SHADER_TYPE) === this.FRAGMENT_SHADER &&
              /#define OPAQUE\b/.test(this.getShaderSource(shader))));
          }
          const diffuse = this.getUniformLocation(program, 'diffuse');
          if (diffuse !== null) window.diffuseColors.add(Array.from(this.getUniform(program, diffuse)).map(v => Math.round(v * 1e6) / 1e6).join(','));
          const location = this.getUniformLocation(program, 'opacity');
          if (location !== null && this.getUniform(program, location) < 1 && opaquePrograms.get(program)) {
            window.badAlphaDraws++;
          }
          return draw.apply(this, args);
        };
      }
      window.AnatomyBridge = { postMessage: value => window.messages.push(JSON.parse(value)) };
    });
    await page.goto(pathToFileURL(path.resolve('assets/viewer/index.html')).href);
    await page.waitForFunction(() => window.anatomy?.ready);
    await page.evaluate(() => window.anatomy.configure({ reducedMotion: true, loading: false, findings: { lung_left: 'danger', lung_right: 'warning' } }));
    await page.screenshot({ path: '.research/anatomy-full.png' });
    await page.evaluate(() => window.anatomy.focus('lung_left'));
    await page.waitForTimeout(100);
    await page.screenshot({ path: '.research/anatomy-focus.png' });
    await page.mouse.click(195, 265);
    assert.ok(await page.evaluate(() => window.messages.some(m => m.type === 'select' && m.value === 'lung_left')), 'Lung mesh should be tappable');
    const manifest = JSON.parse(fs.readFileSync('assets/viewer/anatomy-manifest.json', 'utf8'));
    const dart = fs.readFileSync('lib/main.dart', 'utf8');
    for (const id of Object.keys(manifest).filter(id => id !== 'body_shell')) {
      assert.ok(dart.includes(`'${id}':`), `Missing Flutter selection label for ${id}`);
      assert.ok(manifest[id].triangles > 0, `Empty organ: ${id}`);
    }
    for (const id of ['brain', 'small_intestine', 'kidney_left']) {
      await page.evaluate(id => window.anatomy.focus(id), id);
      // Search a small central grid: hollow anatomical surfaces need not intersect the exact center ray.
      let found = false;
      for (const [x, y] of [[195,265], [180,250], [210,280], [180,280], [210,250]]) {
        await page.mouse.click(x, y);
        found = await page.evaluate(id => window.messages.some(m => m.type === 'select' && m.value === id), id);
        if (found) break;
        await page.evaluate(id => window.anatomy.focus(id), id);
      }
      assert.ok(found, `New organ must be tappable: ${id}`);
    }
    await page.evaluate(() => { window.anatomy.reset(); window.anatomy.configure({ reducedMotion: true, loading: false, organOpacity: 1 }); });
    const opaque = await page.screenshot({ path: '.research/anatomy-neutral.png' });
    await page.evaluate(() => window.anatomy.configure({ reducedMotion: true, loading: false, organOpacity: 0.35 }));
    const transparent = await page.screenshot();
    assert.notDeepEqual(opaque, transparent, 'Opacity control must change the rendered image');
    assert.equal(await page.evaluate(() => window.badAlphaDraws), 0, 'Translucent organs must not use an OPAQUE shader');
    // Allow control damping to settle before checking that idle scenes stop GPU draws.
    await page.waitForTimeout(1000);
    const idleDraws = await page.evaluate(() => window.drawCount);
    await page.waitForTimeout(200);
    assert.equal(await page.evaluate(() => window.drawCount), idleDraws, 'Idle reduced-motion view must not redraw');
    await page.evaluate(() => window.anatomy.nudge('left'));
    const rotated = await page.screenshot();
    assert.notDeepEqual(rotated, transparent, 'Accessible rotate control must move the model');
    await page.evaluate(() => window.anatomy.nudge('in'));
    assert.notDeepEqual(await page.screenshot(), rotated, 'Accessible zoom control must move the camera');
    await page.evaluate(() => window.anatomy.focus('lung_left'));
    const tapCount = await page.evaluate(() => window.messages.filter(m => m.type === 'select').length);
    await page.mouse.move(195, 265);
    await page.mouse.down();
    await page.mouse.move(230, 265, { steps: 3 });
    await page.mouse.move(195, 265, { steps: 3 });
    await page.mouse.up();
    assert.equal(await page.evaluate(() => window.messages.filter(m => m.type === 'select').length), tapCount, 'Out-and-back drag must not select');
    await page.evaluate(() => { window.anatomy.configure({ reducedMotion: true, loading: true }); window.anatomy.focus('lung_left'); });
    await page.mouse.click(195, 265);
    assert.equal(await page.evaluate(() => window.messages.filter(m => m.type === 'select').length), tapCount, 'Loading must suppress organ taps');
    await page.evaluate(() => { window.anatomy.configure({ reducedMotion: true, loading: false }); window.anatomy.reset(); });
    const before = await page.evaluate(() => window.messages.filter(m => m.type === 'select').length);
    await page.mouse.move(140, 210);
    await page.mouse.down();
    await page.mouse.move(220, 250, { steps: 10 });
    await page.mouse.up();
    assert.equal(await page.evaluate(() => window.messages.filter(m => m.type === 'select').length), before, 'Dragging must not select');
    // Isolate mode checks from the preceding drag's residual OrbitControls damping.
    await page.reload();
    await page.waitForFunction(() => window.anatomy?.ready);
    await page.evaluate(() => window.anatomy.configure({ mode: 'muscles', reducedMotion: true, loading: false, organOpacity: 1 }));
    await page.waitForFunction(async () => {
      const before = window.drawCount;
      await new Promise(resolve => setTimeout(resolve, 200));
      return window.drawCount === before;
    }); // Compare only after the preceding drag's control damping settles.
    await page.screenshot({ path: '.research/anatomy-muscles-front.png' });
    const muscleDraws = await page.evaluate(() => window.drawCount);
    await page.evaluate(() => { window.anatomy.focus('lung_left'); window.anatomy.focus('bone_femur_left'); });
    await page.waitForTimeout(200);
    assert.equal(await page.evaluate(() => window.drawCount), muscleDraws, 'Hidden organs cannot trigger focus rendering in muscle mode');
    const muscleIds = Object.keys(manifest).filter(id => id.startsWith('muscle_'));
    assert.equal(muscleIds.length, 28);
    for (const id of muscleIds) {
      await page.evaluate(id => { window.messages = []; window.anatomy.focus(id); }, id);
      let found = false;
      for (const [x, y] of [[195,265], [180,250], [210,280], [165,235], [225,295], [195,220], [195,310]]) {
        await page.mouse.click(x, y);
        found = await page.evaluate(id => window.messages.some(m => m.type === 'select' && m.value === id), id);
        if (found) break;
        await page.evaluate(id => window.anatomy.focus(id), id);
      }
      assert.ok(found, `Muscle must be individually tappable: ${id}`);
      assert.ok(await page.evaluate(() => window.messages.every(m => m.type !== 'select' || m.value.startsWith('muscle_'))), 'Hidden organs must not intercept muscle taps');
    }
    await page.evaluate(() => window.anatomy.focus('muscle_trapezius_left'));
    await page.screenshot({ path: '.research/anatomy-muscles-focus.png' });
    await page.evaluate(() => { window.anatomy.reset(); for (let i = 0; i < 12; i++) window.anatomy.nudge('left'); });
    await page.screenshot({ path: '.research/anatomy-muscles-back.png' });
    await page.evaluate(() => window.anatomy.configure({ mode: 'bones', reducedMotion: true, loading: false }));
    await page.waitForFunction(async () => {
      const before = window.drawCount;
      await new Promise(resolve => setTimeout(resolve, 200));
      return window.drawCount === before;
    });
    await page.screenshot({ path: '.research/anatomy-bones-front.png' });
    const boneDraws = await page.evaluate(() => window.drawCount);
    await page.evaluate(() => { window.anatomy.focus('lung_left'); window.anatomy.focus('muscle_deltoid_left'); });
    await page.waitForTimeout(200);
    assert.equal(await page.evaluate(() => window.drawCount), boneDraws, 'Other modes cannot trigger focus rendering in bones mode');
    const boneIds = Object.keys(manifest).filter(id => id.startsWith('bone_'));
    assert.equal(boneIds.length, 33);
    for (const id of boneIds) {
      await page.evaluate(id => { window.messages = []; window.anatomy.focus(id); }, id);
      let found = false;
      // Group centers can be empty space (ribs, skull, hands), so probe a small grid.
      for (const y of [265, 235, 295, 205, 325, 175, 355]) {
        for (const x of [195, 165, 225, 135, 255]) {
          await page.mouse.click(x, y);
          found = await page.evaluate(id => window.messages.some(m => m.type === 'select' && m.value === id), id);
          if (found) break;
          await page.evaluate(id => window.anatomy.focus(id), id);
        }
        if (found) break;
      }
      assert.ok(found, `Bone/group must be individually tappable: ${id}`);
      assert.ok(await page.evaluate(() => window.messages.every(m => m.type !== 'select' || m.value.startsWith('bone_'))), 'Hidden organs/muscles must not intercept bone taps');
    }
    await page.evaluate(() => window.anatomy.focus('bone_femur_left'));
    await page.screenshot({ path: '.research/anatomy-bones-focus.png' });
    await page.evaluate(() => { window.anatomy.reset(); for (let i = 0; i < 12; i++) window.anatomy.nudge('left'); });
    await page.screenshot({ path: '.research/anatomy-bones-back.png' });
    await page.evaluate(() => window.anatomy.configure({ mode: 'body', reducedMotion: true, loading: false }));
    await page.waitForFunction(async () => {
      const before = window.drawCount;
      await new Promise(resolve => setTimeout(resolve, 200));
      return window.drawCount === before;
    });
    const bodyDraws = await page.evaluate(() => window.drawCount);
    await page.evaluate(() => { window.anatomy.focus('muscle_deltoid_left'); window.anatomy.focus('bone_femur_left'); });
    await page.waitForTimeout(200);
    assert.equal(await page.evaluate(() => window.drawCount), bodyDraws, 'Hidden muscles cannot trigger focus rendering in body mode');
    await page.evaluate(() => {
      window.diffuseColors.clear();
      window.anatomy.reset();
      window.anatomy.configure({ reducedMotion: true, loading: false, organOpacity: 1,
        findings: { lung_left: 'danger', lung_right: 'warning' },
        style: { background: '#f4f1ea', backgroundHighlight: '#ffffff', foreground: '#112233', bodyShell: '#235678',
          danger: '#ffff00', warning: '#00ff00', neutralOrgan: '#0000ff', organColors: { brain: '#ff0000' } },
      });
    });
    await page.screenshot({ path: '.research/anatomy-custom-theme.png' });
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--scene-background')), '#f4f1ea');
    const diffuseColors = await page.evaluate(() => [...window.diffuseColors]);
    for (const color of ['1,0,0', '1,1,0', '0,1,0', '0,0,1']) assert.ok(diffuseColors.includes(color), `Missing themed RGB uniform: ${color}`);
    await page.evaluate(() => window.anatomy.configure({ reducedMotion: true, loading: false, style: { background: 'url(https://invalid.example)' } }));
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--scene-background')), '#f4f1ea', 'Invalid color must not replace a safe CSS value');
    assert.deepEqual(errors, []);
    console.log('PASS: offline GLB, 28 muscle and 33 bone/group selections, mode isolation, organ picking/labels, correct alpha shader, idle GPU, accessible controls, loading guard, drag rejection, custom theme uniforms, no JS errors');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
