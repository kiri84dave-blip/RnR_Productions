"""Procedural Eve + optional GLB stage as a Gradio HTML component."""

from __future__ import annotations

import json

import gradio as gr

HTML_TEMPLATE = """
<div class="stage" id="ara-stage">
  <canvas id="ara-canvas"></canvas>
  <div class="hud">${value && value.name ? value.name : "Ara-Elizabeth"} · ${value && value.action ? value.action : "idle"} · ${value && value.emotion ? value.emotion : "neutral"}</div>
</div>
"""

CSS_TEMPLATE = """
.stage {
  position: relative;
  width: 100%;
  height: 520px;
  background: radial-gradient(ellipse at 50% 20%, #2a2030 0%, #0c0a10 70%);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #3a2a38;
}
#ara-canvas { width: 100%; height: 100%; display: block; }
.hud {
  position: absolute;
  left: 12px;
  bottom: 10px;
  font: 11px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #e8c4c4;
  opacity: 0.85;
}
"""

JS_ON_LOAD = r"""
const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js";
const GLTF_URL = "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js";

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if ([...document.scripts].some((s) => s.src === src)) return resolve();
    const el = document.createElement("script");
    el.src = src;
    el.onload = resolve;
    el.onerror = reject;
    document.head.appendChild(el);
  });
}

function damp(cur, target, lambda, dt) {
  return cur + (target - cur) * (1 - Math.exp(-lambda * dt));
}

function buildEve(THREE) {
  const root = new THREE.Group();
  const skin = new THREE.MeshStandardMaterial({ color: 0xd9b09a, roughness: 0.48, metalness: 0.04 });
  const hair = new THREE.MeshStandardMaterial({ color: 0x1a1216, roughness: 0.35 });
  const dress = new THREE.MeshStandardMaterial({ color: 0x1c1c2c, roughness: 0.55, metalness: 0.12 });
  const lingerie = new THREE.MeshStandardMaterial({ color: 0x4a1020, roughness: 0.4, metalness: 0.2 });
  const trim = new THREE.MeshStandardMaterial({ color: 0xe94560, roughness: 0.4, emissive: 0xe94560, emissiveIntensity: 0.15 });
  const eyeWhite = new THREE.MeshStandardMaterial({ color: 0xf4efe8, roughness: 0.3 });
  const eyeIris = new THREE.MeshStandardMaterial({ color: 0x3a2a28, roughness: 0.2, emissive: 0xe94560, emissiveIntensity: 0.08 });

  const hips = new THREE.Group(); hips.position.set(0, 0.92, 0);
  const dressMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.14, 0.48, 14), dress);
  dressMesh.position.set(0, -0.2, 0); dressMesh.name = "dress";
  const lingerMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.12, 0.22, 14), lingerie);
  lingerMesh.position.set(0, -0.08, 0); lingerMesh.name = "lingerie"; lingerMesh.visible = false;
  hips.add(new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 12), dress));
  const spine = new THREE.Group(); spine.position.set(0, 0.08, 0);
  spine.add(new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.2, 6, 12), dress));
  spine.add(dressMesh); spine.add(lingerMesh);
  const ribbon = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.015, 0.01), trim); ribbon.position.set(0, 0.22, 0.12);
  spine.add(ribbon);
  const chest = new THREE.Group(); chest.position.set(0, 0.28, 0);
  chest.add(new THREE.Mesh(new THREE.CapsuleGeometry(0.11, 0.08, 6, 12), skin));
  const neck = new THREE.Group(); neck.position.set(0, 0.2, 0);
  neck.add(new THREE.Mesh(new THREE.CapsuleGeometry(0.04, 0.07, 4, 8), skin));
  const head = new THREE.Group(); head.position.set(0, 0.16, 0);
  head.add(new THREE.Mesh(new THREE.SphereGeometry(0.115, 20, 16), skin));
  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 10), skin); jaw.position.set(0, -0.06, 0.02); jaw.name = "jaw";
  head.add(jaw);
  head.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(0.13, 16, 12), hair), { position: new THREE.Vector3(0, 0.08, -0.02) }));
  const lEye = new THREE.Mesh(new THREE.SphereGeometry(0.018, 8, 8), eyeWhite); lEye.position.set(0.035, 0.02, 0.1);
  const rEye = lEye.clone(); rEye.position.x = -0.035;
  const lIris = new THREE.Mesh(new THREE.SphereGeometry(0.01, 8, 8), eyeIris); lIris.position.set(0.035, 0.02, 0.115); lIris.name = "lIris";
  const rIris = lIris.clone(); rIris.position.x = -0.035; rIris.name = "rIris";
  head.add(lEye, rEye, lIris, rIris);
  neck.add(head); chest.add(neck); spine.add(chest); hips.add(spine);

  function limb(upperLen, lowerLen, thigh=false) {
    const u = new THREE.Group();
    const um = new THREE.Mesh(new THREE.CapsuleGeometry(thigh ? 0.055 : 0.04, upperLen, 4, 8), thigh ? dress : skin);
    um.position.y = -upperLen / 2; u.add(um);
    const f = new THREE.Group(); f.position.y = -upperLen;
    const fm = new THREE.Mesh(new THREE.CapsuleGeometry(thigh ? 0.042 : 0.032, lowerLen, 4, 8), skin);
    fm.position.y = -lowerLen / 2; f.add(fm);
    u.add(f);
    return { u, f };
  }
  const lArm = limb(0.28, 0.26); lArm.u.position.set(0.16, 0.18, 0); chest.add(lArm.u);
  const rArm = limb(0.28, 0.26); rArm.u.position.set(-0.16, 0.18, 0); chest.add(rArm.u);
  const lLeg = limb(0.32, 0.3, true); lLeg.u.position.set(0.08, 0, 0); hips.add(lLeg.u);
  const rLeg = limb(0.32, 0.3, true); rLeg.u.position.set(-0.08, 0, 0); hips.add(rLeg.u);
  root.add(hips);
  root.userData = { hips, spine, chest, neck, head, jaw, lArm: lArm.u, lFore: lArm.f, rArm: rArm.u, rFore: rArm.f, lThigh: lLeg.u, lShin: lLeg.f, rThigh: rLeg.u, rShin: rLeg.f, dressMesh, lingerMesh, eyeIris, lIris, rIris };
  return root;
}

async function boot() {
  await loadScript(THREE_URL);
  await loadScript(GLTF_URL);
  const THREE = window.THREE;
  const canvas = element.querySelector("#ara-canvas");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
  camera.position.set(0, 1.15, 3.4);
  scene.add(new THREE.HemisphereLight(0xffe8dc, 0x1a1020, 1.1));
  const key = new THREE.DirectionalLight(0xffd0c8, 1.2); key.position.set(2.2, 3.4, 2.4); scene.add(key);
  const rim = new THREE.PointLight(0xe94560, 0.55, 8); rim.position.set(-1.4, 1.6, 1.2); scene.add(rim);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(1.6, 32), new THREE.MeshStandardMaterial({ color: 0x161018, roughness: 0.9 }));
  floor.rotation.x = -Math.PI / 2; scene.add(floor);

  const eve = buildEve(THREE);
  scene.add(eve);
  let glb = null;
  let lastGlb = "";
  const clock = new THREE.Clock();
  const sit = { v: 0 }, walk = { v: 0 }, wave = { v: 0 };

  function resize() {
    const w = canvas.clientWidth || element.clientWidth || 480;
    const h = canvas.clientHeight || 520;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  async function maybeGlb(url) {
    if (!url || url === lastGlb) return;
    lastGlb = url;
    if (glb) { scene.remove(glb); glb = null; }
    try {
      const loader = new THREE.GLTFLoader();
      glb = await new Promise((res, rej) => loader.load(url, (g) => res(g.scene), undefined, rej));
      glb.position.set(0, 0, 0);
      const box = new THREE.Box3().setFromObject(glb);
      const size = box.getSize(new THREE.Vector3()).y || 1;
      glb.scale.setScalar(1.6 / size);
      scene.add(glb);
      eve.visible = false;
    } catch (err) {
      eve.visible = true;
    }
  }

  function applyPose(dt, v) {
    const action = v.action || "idle";
    const emotion = v.emotion || "neutral";
    const intimate = !!v.intimate;
    const clothing = v.clothing || "dressed";
    const d = eve.userData;
    const t = clock.elapsedTime;
    sit.v = damp(sit.v, action === "sit" ? 1 : 0, 4, dt);
    walk.v = damp(walk.v, (action === "walk" || action === "dance") ? 1 : 0, 5, dt);
    wave.v = damp(wave.v, action === "wave" ? 1 : 0, 6, dt);
    const sad = emotion === "sad" ? 1 : 0;
    const happy = (emotion === "happy" || emotion === "excited") ? 1 : 0;
    const shy = emotion === "shy" ? 1 : 0;
    const playful = emotion === "playful" ? 1 : 0;
    const excited = emotion === "excited" ? 1 : 0;
    const breathe = Math.sin(t * 1.5) * 0.02;
    const w = t * (action === "dance" ? 5.2 : 6.2);
    const stride = Math.sin(w) * walk.v;
    const stride2 = Math.sin(w + Math.PI) * walk.v;
    eve.position.y = damp(eve.position.y, (sit.v * -0.42) + Math.abs(Math.sin(w)) * 0.04 * walk.v, 6, dt);
    eve.rotation.y = damp(eve.rotation.y, action === "walk" ? t * 0.35 : 0.22, 3, dt);
    d.spine.rotation.x = breathe * 2 - 0.12 * sad + 0.06 * happy - 0.55 * sit.v;
    if (intimate && action === "bend_over") d.spine.rotation.x = 0.95;
    if (intimate && action === "spread_legs") d.hips.rotation.z = 0.08;
    d.head.rotation.x = -0.08 * sad + 0.12 * shy + (action === "think" ? 0.18 : 0) + (action === "nod" ? Math.sin(t * 5) * 0.18 : 0);
    d.head.rotation.z = shy * 0.15 + playful * Math.sin(t * 2) * 0.08;
    if (action === "wink" && intimate) d.lIris.scale.set(1, 0.15, 1); else d.lIris.scale.set(1, 1, 1);
    d.rArm.rotation.x = 0.18 + stride * 0.55 + (action === "think" ? -1.6 : 0) + (action === "stretch" ? -2.6 : 0) + (action === "pose" ? -0.4 : 0) + (wave.v > 0.05 ? -2.4 * wave.v : 0);
    d.lArm.rotation.x = 0.18 + stride2 * 0.55 + (action === "stretch" ? -2.6 : 0);
    d.rArm.rotation.z = wave.v > 0.05 ? Math.sin(t * 9) * 0.45 * wave.v : -0.12;
    d.lThigh.rotation.x = stride * 0.7 + sit.v * -1.45 + ((intimate && action === "spread_legs") ? -0.7 : 0) + ((intimate && action === "kneel") ? -1.2 : 0);
    d.rThigh.rotation.x = stride2 * 0.7 + sit.v * -1.45 + ((intimate && action === "spread_legs") ? -0.7 : 0) + ((intimate && action === "kneel") ? -1.2 : 0);
    d.dressMesh.visible = clothing !== "nude";
    d.lingerMesh.visible = clothing === "lingerie" || clothing === "nude";
    if (clothing === "nude") { d.dressMesh.visible = false; }
    d.eyeIris.emissiveIntensity = 0.08 + happy * 0.25 + excited * 0.35 + playful * 0.2;
    if (glb) {
      glb.rotation.y = eve.rotation.y;
      glb.rotation.x = (intimate && action === "bend_over") ? 0.7 : 0;
      glb.position.y = eve.position.y;
    }
  }

  function loop() {
    const dt = Math.min(clock.getDelta(), 0.1);
    const v = props.value || {};
    maybeGlb(v.glbUrl || "");
    applyPose(dt, v);
    renderer.render(scene, camera);
    requestAnimationFrame(loop);
  }
  loop();
}
boot();
"""


class AvatarStage(gr.HTML):
    def __init__(self, value: dict | None = None, **kwargs):
        super().__init__(
            value=value or {"action": "look", "emotion": "happy", "clothing": "dressed", "name": "Ara-Elizabeth"},
            html_template=HTML_TEMPLATE,
            css_template=CSS_TEMPLATE,
            js_on_load=JS_ON_LOAD,
            **kwargs,
        )

    def api_info(self):
        return {"type": "object"}


def dumps(payload: dict) -> str:
    return json.dumps(payload)
