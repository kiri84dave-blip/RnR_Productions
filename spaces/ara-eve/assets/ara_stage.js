import * as THREE from "/ara-assets/three.module.min.js";
import { GLTFLoader } from "/ara-assets/GLTFLoader.js";

const CLIP_FOR_ACTION = {
  idle: "Idle_Sword",
  look: "Idle_Sword",
  nod: "Idle_Sword",
  sit: "Sitting_Enter",
  think: "Meditate",
  pose: "Bow",
  wink: "Bow",
  wave: "Hit_Head",
  walk: "Jump_2",
  dance: "Jump_2",
  stretch: "Jump_Land",
  kneel: "Kneeling_Tired",
  bend_over: "Kneeling_Tired",
  spread_legs: "Kneeling_Tired",
};

export async function bootGlb(element, props) {
  const canvas = element.querySelector("#ara-webgl");
  const fallback = element.querySelector("#ara-canvas");
  if (!canvas) return false;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(28, 1, 0.05, 40);
  camera.position.set(0, 1.15, 3.15);
  scene.add(new THREE.HemisphereLight(0xffe8dc, 0x1a1020, 1.15));
  const key = new THREE.DirectionalLight(0xffd0c8, 1.35);
  key.position.set(2.0, 3.2, 2.2);
  scene.add(key);
  const rim = new THREE.PointLight(0xe94560, 0.45, 10);
  rim.position.set(-1.6, 1.4, 1.4);
  scene.add(rim);
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(1.8, 40),
    new THREE.MeshStandardMaterial({ color: 0x141018, roughness: 0.92 }),
  );
  floor.rotation.x = -Math.PI / 2;
  scene.add(floor);

  function resize() {
    const w = Math.max(280, element.clientWidth || 480);
    const h = 520;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  const url = (props.value && props.value.glbUrl) || "/ara-assets/KF1b_anim.glb";
  const loader = new GLTFLoader();
  const gltf = await new Promise((resolve, reject) => loader.load(url, resolve, undefined, reject));
  const model = gltf.scene;
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3());
  const scale = 1.7 / (size.y || 1);
  model.scale.setScalar(scale);
  box.setFromObject(model);
  model.position.y = -box.min.y;
  model.rotation.y = 0.18;
  scene.add(model);

  const mixer = new THREE.AnimationMixer(model);
  const clips = Object.fromEntries((gltf.animations || []).map((c) => [c.name, c]));
  let current = "";
  function play(actionName) {
    const clipName = CLIP_FOR_ACTION[actionName] || "Idle_Sword";
    if (clipName === current) return;
    const clip = clips[clipName] || clips.Idle_Sword;
    if (!clip) return;
    mixer.stopAllAction();
    const act = mixer.clipAction(clip);
    act.reset();
    act.fadeIn(0.2);
    if (clipName === "Sitting_Enter" || clipName === "Bow" || clipName === "Jump_Land") {
      act.setLoop(THREE.LoopOnce, 1);
      act.clampWhenFinished = true;
    }
    act.play();
    current = clipName;
  }
  play((props.value && props.value.action) || "idle");

  if (fallback) fallback.style.display = "none";
  canvas.style.display = "block";

  const clock = new THREE.Clock();
  function loop() {
    const dt = Math.min(clock.getDelta(), 0.08);
    const v = props.value || {};
    play(v.action || "idle");
    mixer.update(dt);
    renderer.render(scene, camera);
    requestAnimationFrame(loop);
  }
  loop();
  return true;
}
