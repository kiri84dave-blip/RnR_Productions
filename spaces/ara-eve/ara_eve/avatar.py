"""Procedural Eve + optional GLB stage as a Gradio HTML component.

Primary renderer is a self-contained 2D canvas so the figure still appears when
CDN Three.js is blocked. GLB URLs try THREE.GLTFLoader when it is available.
"""

from __future__ import annotations

import json

import gradio as gr

HTML_TEMPLATE = """
<div class="stage" id="ara-stage">
  <canvas id="ara-canvas"></canvas>
  <div class="hud">${(value && value.name) ? value.name : "Ara-Elizabeth"} · ${(value && value.action) ? value.action : "idle"} · ${(value && value.emotion) ? value.emotion : "neutral"}</div>
</div>
"""

CSS_TEMPLATE = """
.stage {
  position: relative;
  width: 100%;
  height: 520px;
  background: radial-gradient(ellipse at 50% 18%, #3a2438 0%, #120c14 72%);
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
  opacity: 0.9;
}
"""

JS_ON_LOAD = r"""
const canvas = element.querySelector("#ara-canvas");
const ctx = canvas.getContext("2d");
let t = 0;
let sit = 0, walk = 0, wave = 0;

function resize() {
  const w = Math.max(320, element.clientWidth || 480);
  const h = 520;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + "px";
  canvas.style.height = h + "px";
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
resize();
window.addEventListener("resize", resize);

function damp(cur, target, lambda, dt) {
  return cur + (target - cur) * (1 - Math.exp(-lambda * dt));
}
function lerp(a, b, u) { return a + (b - a) * u; }
function oval(x, y, rx, ry, fill) {
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
}
function limb(x1, y1, x2, y2, width, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}

function draw(v, dt) {
  const w = canvas.clientWidth || 480;
  const h = 520;
  ctx.clearRect(0, 0, w, h);
  const action = (v && v.action) || "idle";
  const emotion = (v && v.emotion) || "neutral";
  const clothing = (v && v.clothing) || "dressed";
  const intimate = !!(v && v.intimate);
  sit = damp(sit, action === "sit" || action === "kneel" ? 1 : 0, 5, dt);
  walk = damp(walk, (action === "walk" || action === "dance") ? 1 : 0, 6, dt);
  wave = damp(wave, action === "wave" ? 1 : 0, 8, dt);
  const sad = emotion === "sad" ? 1 : 0;
  const happy = (emotion === "happy" || emotion === "excited") ? 1 : 0;
  const shy = emotion === "shy" ? 1 : 0;
  const playful = emotion === "playful" ? 1 : 0;
  const cx = w * 0.5;
  const ground = h * 0.88;
  const bounce = Math.abs(Math.sin(t * 8)) * 10 * walk;
  const hipY = lerp(ground - 210, ground - 140, sit) - bounce;
  const hipX = cx + Math.sin(t * 1.6) * 6 * walk;
  const stride = Math.sin(t * 6.2) * 38 * walk;
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.beginPath(); ctx.ellipse(cx, ground + 8, 90, 14, 0, 0, Math.PI * 2); ctx.fill();

  const skin = "#d9b09a";
  const hair = "#1a1216";
  const dress = clothing === "nude" ? skin : (clothing === "lingerie" ? "#4a1020" : "#1c1c2c");
  const trim = "#e94560";

  let lFootX = hipX - 22 + stride;
  let rFootX = hipX + 22 - stride;
  let lKneeY = hipY + 70;
  let rKneeY = hipY + 70;
  if (intimate && action === "spread_legs") { lFootX -= 42; rFootX += 42; }
  if (action === "kneel" && intimate) { lKneeY = ground - 18; rKneeY = ground - 18; }
  limb(hipX - 16, hipY, lFootX, ground - 8 * sit, 16, skin);
  limb(hipX + 16, hipY, rFootX, ground - 8 * sit, 16, skin);

  const bend = (intimate && action === "bend_over") ? 1 : 0;
  const chestY = hipY - 70 + sit * 18 + bend * 40;
  const chestX = hipX + bend * 36;
  ctx.fillStyle = dress;
  ctx.beginPath();
  ctx.moveTo(hipX - 46, hipY + 10);
  ctx.lineTo(hipX + 46, hipY + 10);
  ctx.lineTo(chestX + 34, chestY + 18);
  ctx.lineTo(chestX - 34, chestY + 18);
  ctx.closePath();
  ctx.fill();
  oval(chestX, chestY, 28, 22, skin);
  if (clothing !== "nude") {
    ctx.fillStyle = trim;
    ctx.fillRect(chestX - 18, chestY + 8, 36, 3);
  }

  let lArmX = chestX - 40 - stride * 0.4;
  let rArmX = chestX + 40 + stride * 0.4;
  let lArmY = chestY + 70;
  let rArmY = chestY + 70;
  if (wave > 0.05) { rArmX = chestX + 18; rArmY = chestY - 70 - Math.sin(t * 10) * 18 * wave; }
  if (action === "think") { rArmX = chestX + 12; rArmY = chestY - 28; }
  if (action === "stretch") { lArmY = chestY - 80; rArmY = chestY - 80; }
  if (action === "pose") { rArmX = chestX + 70; rArmY = chestY + 10; lArmX = chestX - 20; }
  limb(chestX - 24, chestY, lArmX, lArmY, 12, skin);
  limb(chestX + 24, chestY, rArmX, rArmY, 12, skin);

  const headY = chestY - 48 - sad * 6 + shy * 4;
  const headX = chestX + Math.sin(t * 0.8) * 4 + (action === "look" ? 10 : 0) + (action === "nod" ? Math.sin(t * 6) * 6 : 0);
  oval(headX, headY - 6, 28, 26, hair);
  oval(headX, headY + 4, 22, 24, skin);
  oval(headX - 22, headY + 8, 8, 16, hair);
  oval(headX + 22, headY + 8, 8, 16, hair);
  const wink = (intimate && action === "wink") ? 1 : 0;
  ctx.fillStyle = "#1a1210";
  ctx.beginPath(); ctx.ellipse(headX - 7, headY + 2, 3.2, wink ? 0.6 : 3.4, 0, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(headX + 7, headY + 2, 3.2, 3.4, 0, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = happy ? trim : "#8a4a4a";
  ctx.lineWidth = 2;
  ctx.beginPath();
  if (sad) { ctx.arc(headX, headY + 16, 7, Math.PI, 0); }
  else { ctx.arc(headX, headY + 10, 7, 0.15, Math.PI - 0.15); }
  ctx.stroke();
  if (playful) {
    ctx.fillStyle = "rgba(233,69,96,0.35)";
    oval(headX - 16, headY + 12, 6, 4, "rgba(233,69,96,0.35)");
    oval(headX + 16, headY + 12, 6, 4, "rgba(233,69,96,0.35)");
  }
}

function loop() {
  const dt = 1 / 60;
  t += dt;
  const v = (props && props.value) ? props.value : {};
  draw(v, dt);
  requestAnimationFrame(loop);
}
loop();
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
