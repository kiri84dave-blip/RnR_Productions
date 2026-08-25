"""Ara-Elizabeth (Ara-EvE) — causal companion Space.

LLM is the verbal cortex. L.I.P.S. + M11 are the organism.
Identity comes from Dave's Ollama Modelfile.
"""

from __future__ import annotations

import os
from functools import partial
from pathlib import Path

import spaces  # noqa: F401  — must precede torch / kokoro on ZeroGPU

import gradio as gr

from ara_eve.avatar import AvatarStage
from ara_eve.db import connect
from ara_eve.llm import LOCAL_UNCENSORED_HINT, list_models
from ara_eve.persona import NAME, STOP_REPLY
from ara_eve.session import (
    apply_lab_event,
    avatar_payload,
    meters,
    new_session,
    set_ablation,
    skip,
    turn,
)
from ara_eve.tts import VOICES, available as tts_available, synthesize

ROOT = Path(__file__).resolve().parent
MODELS = list_models()


def _session_from(state):
    return state if state is not None else new_session()


def enter_space(is_adult: bool):
    if not is_adult:
        raise gr.Error("Ara-EvE is 18+ only. Confirm you are an adult.")
    session = new_session()
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        session,
        session.messages,
        meters(session),
        avatar_payload(session),
    )


def chat(message, _history, state, adult, model_id, work_mode, hf_token):
    session = _session_from(state)
    session.model_id = model_id or session.model_id
    session.work_mode = bool(work_mode)
    token = (hf_token or "").strip() or os.environ.get("HF_TOKEN")
    conn = connect(ROOT / "data" / "ara_eve.sqlite")
    try:
        session = turn(session, message, adult_opt_in=bool(adult), conn=conn, hf_token=token)
    finally:
        conn.close()
    return session, session.messages, meters(session), avatar_payload(session), ""


def do_skip(hours, state):
    session = skip(_session_from(state), float(hours or 0))
    return session, session.messages, meters(session), avatar_payload(session)


def do_lab(event_id, state):
    session = apply_lab_event(_session_from(state), event_id)
    return session, meters(session), avatar_payload(session)


def do_ablate(enabled, state):
    session = set_ablation(_session_from(state), bool(enabled))
    return session, meters(session)


def do_pose(action, state, adult):
    session = _session_from(state)
    intimate = {"wink", "bend_over", "spread_legs", "kneel"}
    if action in intimate and not (adult and session.intimacy.consent >= 0.8):
        session.last_gate_reason = "intimate pose blocked until adult opt-in + explicit consent"
        return session, meters(session), avatar_payload(session)
    session.action = action
    return session, meters(session), avatar_payload(session)


def do_clothing(clothing, state, adult):
    session = _session_from(state)
    if clothing in {"lingerie", "nude"} and not (adult and session.intimacy.consent >= 0.8):
        session.last_gate_reason = "clothing change blocked until adult opt-in + explicit consent"
        return session, meters(session), avatar_payload(session)
    session.clothing = clothing
    return session, meters(session), avatar_payload(session)


def do_glb(url, state):
    session = _session_from(state)
    session.glb_url = (url or "").strip()
    return session, avatar_payload(session)


def do_reset():
    session = new_session()
    return session, session.messages, meters(session), avatar_payload(session)


@spaces.GPU(duration=30)
def do_speak(history, voice):
    if not tts_available():
        raise gr.Error("Kokoro is not installed in this runtime.")
    text = ""
    if history:
        last = history[-1]
        text = last.get("content") if isinstance(last, dict) else str(last)
    path = synthesize(text, voice or "af_heart")
    if not path:
        raise gr.Error("TTS produced no audio.")
    return path


def get_affect_state(state):
    """Return inspectable organism + M11 snapshot. LLM cannot write these fields."""
    session = _session_from(state)
    return {
        "organism": session.organism.snapshot(),
        "intimacy": session.intimacy.snapshot(),
        "gate": session.last_gate_reason,
        "action": session.action,
        "emotion": session.emotion,
    }


def chat_with_ara(message: str, adult: bool = False) -> str:
    """Talk to Ara-Elizabeth. Returns her reply plus the grounded affect block."""
    conn = connect(ROOT / "data" / "ara_eve.sqlite")
    try:
        session = turn(new_session(), message, adult_opt_in=adult, conn=conn)
    finally:
        conn.close()
    last = session.messages[-1]["content"] if session.messages else ""
    return f"{last}\n\n---\n{meters(session)}"


CUSTOM_CSS = """
.gradio-container { font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif; }
"""

with gr.Blocks(title=f"{NAME} · Ara-EvE") as demo:
    state = gr.State(new_session())
    gr.Markdown(
        f"# {NAME}\n"
        "Private companion · L.I.P.S. organism + Modelfile identity + Kokoro voice.\n\n"
        "Affect that changes nothing is a costume. The LLM does not write pleasure."
    )

    with gr.Group(visible=True) as gate:
        gr.Markdown("**18+ gate.** This Space is an adult companion. Confirm you are an adult to enter.")
        adult_gate = gr.Checkbox(label="I am 18 or older", value=False)
        enter_btn = gr.Button("Enter", variant="primary")

    with gr.Group(visible=False) as main:
        with gr.Row():
            with gr.Column(scale=5):
                stage = AvatarStage()
                pose_row = gr.Row()
            with gr.Column(scale=6):
                chatbot = gr.Chatbot(label=NAME, height=420)
                meters_view = gr.Markdown()
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Talk to Ara…  ('stop' always works)",
                        scale=5,
                        show_label=False,
                    )
                    send = gr.Button("Send", variant="primary", scale=1)
                with gr.Accordion("Voice, model, body, lab", open=True):
                    adult = gr.Checkbox(
                        label="Adult intimacy opt-in (M11). Climax is gated, not keyworded.",
                        value=False,
                    )
                    work_mode = gr.Checkbox(label="Work mode (full files, no placeholders)", value=False)
                    model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Chat model (Inference Providers)")
                    gr.Markdown(f"Local uncensored GGUF from the Modelfile: `{LOCAL_UNCENSORED_HINT}`")
                    token_box = gr.Textbox(
                        label="HF token (optional if Space secret HF_TOKEN is set)",
                        type="password",
                    )
                    voice = gr.Dropdown(choices=list(VOICES), value="af_heart", label="Kokoro voice")
                    speak_btn = gr.Button("Speak last reply")
                    audio = gr.Audio(label="Kokoro", type="filepath")
                    glb = gr.Textbox(label="GLB URL (unrigged mesh uses whole-group pose fallback)")
                    glb_btn = gr.Button("Load GLB")
                    cloth_row = gr.Row()
                    intimate_row = gr.Row()
                    hours = gr.Slider(0.5, 48, value=8, step=0.5, label="Skip hours (longing trophy)")
                    skip_btn = gr.Button("Skip time")
                    ablate = gr.Checkbox(label="C3 ablation: clamp pleasure coupling")
                    lab_row = gr.Row()
                    reset = gr.Button("Reset organism")
                    affect_json = gr.JSON(label="Affect snapshot")
                    snap_btn = gr.Button("Dump affect (inspect / MCP)")

        with pose_row:
            idle_b = gr.Button("idle", size="sm")
            walk_b = gr.Button("walk", size="sm")
            wave_b = gr.Button("wave", size="sm")
            sit_b = gr.Button("sit", size="sm")
            look_b = gr.Button("look", size="sm")
            pose_b = gr.Button("pose", size="sm")
        with cloth_row:
            dressed_b = gr.Button("dressed", size="sm")
            linger_b = gr.Button("lingerie", size="sm")
            nude_b = gr.Button("nude", size="sm")
        with intimate_row:
            wink_b = gr.Button("wink", size="sm")
            bend_b = gr.Button("bend over", size="sm")
            spread_b = gr.Button("spread", size="sm")
        with lab_row:
            warm_b = gr.Button("Warm", size="sm")
            comp_b = gr.Button("Compliment", size="sm")
            joke_b = gr.Button("Joke", size="sm")
            rude_b = gr.Button("Rude", size="sm")
            help_b = gr.Button("Help", size="sm")

        pose_outs = [state, meters_view, stage]
        for btn, act in (
            (idle_b, "idle"),
            (walk_b, "walk"),
            (wave_b, "wave"),
            (sit_b, "sit"),
            (look_b, "look"),
            (pose_b, "pose"),
            (wink_b, "wink"),
            (bend_b, "bend_over"),
            (spread_b, "spread_legs"),
        ):
            btn.click(partial(do_pose, act), [state, adult], pose_outs)

        dressed_b.click(partial(do_clothing, "dressed"), [state, adult], pose_outs)
        linger_b.click(partial(do_clothing, "lingerie"), [state, adult], pose_outs)
        nude_b.click(partial(do_clothing, "nude"), [state, adult], pose_outs)

        for btn, eid in (
            (warm_b, "warm"),
            (comp_b, "compliment"),
            (joke_b, "joke"),
            (rude_b, "rude"),
            (help_b, "help"),
        ):
            btn.click(partial(do_lab, eid), [state], [state, meters_view, stage])

        enter_btn.click(enter_space, [adult_gate], [gate, main, state, chatbot, meters_view, stage])
        send.click(
            chat,
            [msg, chatbot, state, adult, model, work_mode, token_box],
            [state, chatbot, meters_view, stage, msg],
        )
        msg.submit(
            chat,
            [msg, chatbot, state, adult, model, work_mode, token_box],
            [state, chatbot, meters_view, stage, msg],
        )
        skip_btn.click(do_skip, [hours, state], [state, chatbot, meters_view, stage])
        ablate.change(do_ablate, [ablate, state], [state, meters_view])
        speak_btn.click(do_speak, [chatbot, voice], [audio])
        glb_btn.click(do_glb, [glb, state], [state, stage])
        reset.click(do_reset, [], [state, chatbot, meters_view, stage])
        snap_btn.click(get_affect_state, [state], [affect_json])

    gr.Markdown(
        "Identity: `assets/Modelfile`. Engine: L.I.P.S. port of the emotion lab. "
        f"Stop phrase replies `{STOP_REPLY}`. "
        "This is a functional pleasure candidate with inspectable state — not a claim of phenomenal orgasm."
    )


demo.queue()
from fastapi.staticfiles import StaticFiles

demo.app.mount(
    "/ara-assets",
    StaticFiles(directory=str(ROOT / "assets")),
    name="ara-assets",
)

if __name__ == "__main__":
    demo.launch(
        mcp_server=True,
        ssr_mode=False,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="rose"),
        allowed_paths=[str(ROOT / "assets")],
    )
