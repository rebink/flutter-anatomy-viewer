import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const status = document.getElementById('status');
const send = (type, value = '') => window.AnatomyBridge?.postMessage(JSON.stringify({ type, value }));
const meshes = new Map();
const colors = { warning: 0xffbd68, danger: 0xff6e73 };
const appearance = {
  bodyShell: 0x75cedb, neutralOrgan: 0x80c6d0, warning: colors.warning, danger: colors.danger,
  background: 0x08191f, backgroundHighlight: 0x14323b, foreground: 0xb5d8d8,
  keyLight: 0xd5f6ff, rimLight: 0x41bbb7, ambientSky: 0xc5ffff, ambientGround: 0x143240,
};
const sceneLights = {};
let shellMaterial;
// Anatomy colors distinguish structures, not health status.
let anatomyColors = {
  brain: 0xb9dfd5, airway: 0x89dcf1, esophagus: 0x759bd5,
  lung_left: 0x60d7c2, lung_right: 0x60d7c2, heart: 0x9ebcfa,
  liver: 0x548fb5, stomach: 0xa4e4be, small_intestine: 0x66cba1,
  large_intestine: 0xb0e1cd, kidney_left: 0x8caedf, kidney_right: 0x8caedf,
  bladder: 0x98d5ea, pancreas: 0xc4d9c8, gallbladder: 0x76c9bb,
};
let mode = 'body';
const isMuscle = id => id.startsWith('muscle_');
const isBone = id => id.startsWith('bone_');
const inMode = id => (isMuscle(id) ? 'muscles' : isBone(id) ? 'bones' : 'body') === mode;
const posterior = id => /^muscle_(triceps|trapezius|latissimus|gluteus|biceps_femoris|gastrocnemius)_/.test(id)
  || /^bone_(scapula_|spine_|sacrum$)/.test(id);
let organOpacity = 1;
let reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let loading = true;
let paused = false;
let interacted = false;
let tween = null;
let selected = '';
let findings = {};
let renderer, camera, controls, scene;
let needsRender = true;

function fail() {
  status.textContent = '3D view unavailable. Use the findings list below.';
  status.hidden = false;
  send('error');
}

function applyStyle(style) {
  if (!style || typeof style !== 'object' || Array.isArray(style)) return;
  const validColor = value => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);
  for (const key of Object.keys(appearance)) {
    if (validColor(style[key])) appearance[key] = parseInt(style[key].slice(1), 16);
  }
  if (style.organColors && typeof style.organColors === 'object' && !Array.isArray(style.organColors)) {
    anatomyColors = Object.fromEntries(Object.entries(style.organColors)
      .filter(([id, color]) => meshes.has(id) && validColor(color))
      .map(([id, color]) => [id, parseInt(color.slice(1), 16)]));
  }
  colors.warning = appearance.warning;
  colors.danger = appearance.danger;
  shellMaterial?.uniforms.tint.value.setHex(appearance.bodyShell);
  sceneLights.key?.color.setHex(appearance.keyLight);
  sceneLights.rim?.color.setHex(appearance.rimLight);
  sceneLights.ambient?.color.setHex(appearance.ambientSky);
  sceneLights.ambient?.groundColor.setHex(appearance.ambientGround);
  for (const [variable, key] of [['background', 'background'], ['highlight', 'backgroundHighlight'], ['foreground', 'foreground']]) {
    document.documentElement.style.setProperty(`--scene-${variable}`, `#${appearance[key].toString(16).padStart(6, '0')}`);
  }
}

function paint() {
  needsRender = true;
  for (const [id, mesh] of meshes) {
    mesh.visible = inMode(id);
    const color = selected === id && (isMuscle(id) || isBone(id)) ? 0xffd58a
      : colors[findings[id]] ?? anatomyColors[id] ?? (isMuscle(id) ? 0xc77665 : isBone(id) ? 0xe4d8b8 : appearance.neutralOrgan);
    mesh.material.color.setHex(color);
    mesh.material.emissive.setHex(color);
    mesh.material.emissiveIntensity = selected === id ? 0.45 : 0.12;
    const opacity = selected && selected !== id ? Math.min(organOpacity, 0.12) : organOpacity;
    mesh.material.opacity = opacity;
    const transparent = opacity < 1;
    if (mesh.material.transparent !== transparent) {
      mesh.material.transparent = transparent;
      mesh.material.needsUpdate = true;
    }
    mesh.material.depthWrite = opacity === 1;
    mesh.renderOrder = selected === id ? 2 : 1;
  }
}

function move(position, target) {
  controls.autoRotate = false;
  tween = { position, target };
  if (reducedMotion) {
    camera.position.copy(position);
    controls.target.copy(target);
    tween = null;
    controls.update();
  }
}

window.anatomy = {
  configure(config) {
    if (!config || typeof config !== 'object') return;
    applyStyle(config.style);
    reducedMotion = config.reducedMotion === true;
    if (['body', 'muscles', 'bones'].includes(config.mode) && config.mode !== mode) {
      mode = config.mode;
      window.anatomy.reset();
    }
    const nextLoading = config.loading === true;
    if (nextLoading && !loading) {
      window.anatomy.reset();
      interacted = false;
    }
    loading = nextLoading;
    if (typeof config.organOpacity === 'number' && Number.isFinite(config.organOpacity)) {
      organOpacity = THREE.MathUtils.clamp(config.organOpacity, 0.35, 1);
    }
    findings = {};
    for (const [id, value] of Object.entries(config.findings ?? {})) {
      if (meshes.has(id) && ['neutral', 'warning', 'danger'].includes(value)) findings[id] = value;
    }
    if (controls) controls.autoRotate = loading && !reducedMotion && !interacted;
    if (tween && reducedMotion) move(tween.position, tween.target);
    paint();
  },
  focus(id) {
    const mesh = meshes.get(id);
    if (!mesh || !inMode(id)) return;
    selected = id;
    paint();
    const center = new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
    const size = new THREE.Box3().setFromObject(mesh).getSize(new THREE.Vector3());
    const distance = isMuscle(id) || isBone(id) ? Math.max(isBone(id) ? 0.4 : 0.65, size.length() * 1.8) : 0.65;
    const elevation = id.startsWith('bone_foot_') ? distance * 0.6 : 0.015;
    move(center.clone().add(new THREE.Vector3(0, elevation, posterior(id) ? -distance : distance)), center);
  },
  reset() {
    selected = '';
    paint();
    if (camera) move(new THREE.Vector3(0, 0.82, 2.7), new THREE.Vector3(0, 0.82, 0.09));
  },
  nudge(action) {
    if (!camera || !['left', 'right', 'in', 'out'].includes(action)) return;
    interacted = true;
    const offset = camera.position.clone().sub(controls.target);
    if (action === 'left' || action === 'right') {
      offset.applyAxisAngle(new THREE.Vector3(0, 1, 0), action === 'left' ? -Math.PI / 12 : Math.PI / 12);
    } else {
      offset.setLength(THREE.MathUtils.clamp(offset.length() * (action === 'in' ? 0.8 : 1.25), controls.minDistance, controls.maxDistance));
    }
    move(controls.target.clone().add(offset), controls.target.clone());
  },
  pause(value) { paused = value === true; needsRender = true; },
};

try {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 0.01, 20);
  camera.position.set(0, 0.82, 2.7);
  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'Rotatable anatomical body. Select organs, major muscles or bones using the app list.');
  renderer.domElement.addEventListener('webglcontextlost', event => { event.preventDefault(); paused = true; fail(); });
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0.82, 0.09);
  controls.enablePan = false;
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.minDistance = 0.35;
  controls.maxDistance = 3.8;
  controls.minPolarAngle = 0.5;
  controls.maxPolarAngle = Math.PI - 0.5;
  controls.autoRotateSpeed = 0.55;
  controls.addEventListener('start', () => { interacted = true; controls.autoRotate = false; tween = null; });
  controls.addEventListener('change', () => { needsRender = true; });
  sceneLights.ambient = new THREE.HemisphereLight(appearance.ambientSky, appearance.ambientGround, 2.0);
  scene.add(sceneLights.ambient);
  const key = sceneLights.key = new THREE.DirectionalLight(appearance.keyLight, 2.6);
  key.position.set(-1, 2, 3);
  scene.add(key);
  const rim = sceneLights.rim = new THREE.DirectionalLight(appearance.rimLight, 2.5);
  rim.position.set(2, 1, -1);
  scene.add(rim);

  const bytes = Uint8Array.from(atob(window.ANATOMY_GLB), char => char.charCodeAt(0));
  delete window.ANATOMY_GLB;
  new GLTFLoader().parse(bytes.buffer, '', gltf => {
    gltf.scene.traverse(mesh => {
      if (!mesh.isMesh) return;
      mesh.geometry.computeVertexNormals();
      if (mesh.name === 'body_shell') {
        mesh.material = shellMaterial = new THREE.ShaderMaterial({
          transparent: true, depthWrite: false, side: THREE.FrontSide,
          uniforms: { tint: { value: new THREE.Color(appearance.bodyShell) } },
          vertexShader: `varying vec3 n; varying vec3 v;
            void main(){ vec4 p=modelViewMatrix*vec4(position,1.0);
              n=normalize(normalMatrix*normal); v=normalize(-p.xyz); gl_Position=projectionMatrix*p; }`,
          fragmentShader: `uniform vec3 tint; varying vec3 n; varying vec3 v;
            void main(){float edge=pow(1.0-abs(dot(normalize(n),normalize(v))),2.5);
              gl_FragColor=vec4(tint,0.018+edge*0.28);}`,
        });
        mesh.renderOrder = 10;
      } else {
        mesh.material = new THREE.MeshStandardMaterial({ roughness: 0.55, metalness: 0.04 });
        meshes.set(mesh.name, mesh);
      }
    });
    scene.add(gltf.scene);
    applyStyle(appearance);
    paint();
    status.hidden = true;
    controls.autoRotate = loading && !reducedMotion && !interacted;
    window.anatomy.ready = true;
    send('ready');
  }, fail);

  const pointer = new THREE.Vector2();
  const ray = new THREE.Raycaster();
  let down = null;
  const pointers = new Set();
  renderer.domElement.addEventListener('pointerdown', e => {
    pointers.add(e.pointerId);
    down = pointers.size === 1 ? { x: e.clientX, y: e.clientY, time: performance.now() } : null;
  });
  renderer.domElement.addEventListener('pointermove', e => {
    if (down && Math.hypot(e.clientX - down.x, e.clientY - down.y) > 8) down = null;
  });
  renderer.domElement.addEventListener('pointercancel', e => { pointers.delete(e.pointerId); down = null; });
  renderer.domElement.addEventListener('pointerup', e => {
    pointers.delete(e.pointerId);
    if (loading || !down || pointers.size || performance.now() - down.time > 600 || Math.hypot(e.clientX-down.x, e.clientY-down.y) > 8) { down = null; return; }
    down = null;
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.set((e.clientX-rect.left)/rect.width*2-1, -(e.clientY-rect.top)/rect.height*2+1);
    ray.setFromCamera(pointer, camera);
    const hits = ray.intersectObjects([...meshes.values()].filter(mesh => mesh.visible));
    const hit = hits.find(item => item.object.name === selected) ?? hits[0];
    if (hit) { window.anatomy.focus(hit.object.name); send('select', hit.object.name); }
  });
  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
    needsRender = true;
  });
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.05);
    if (paused || document.hidden) return;
    if (tween) {
      const alpha = 1 - Math.exp(-dt * 7);
      camera.position.lerp(tween.position, alpha);
      controls.target.lerp(tween.target, alpha);
      if (camera.position.distanceTo(tween.position) < 0.001) tween = null;
    }
    controls.update(dt);
    if (needsRender) {
      renderer.render(scene, camera);
      needsRender = false;
    }
  });
} catch { fail(); }
