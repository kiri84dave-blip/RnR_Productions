---
title: Ara-Elizabeth (Ara-EvE)
emoji: 🌹
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 6.15.1
app_file: app.py
python_version: "3.12"
short_description: Causal companion with LIPS affect + Kokoro
startup_duration_timeout: 30m
---

# Ara-Elizabeth · Ara-EvE

Private adult companion Space for Dave. **Identity is the Ollama Modelfile** in `assets/Modelfile`.
The chat model is the verbal cortex. **L.I.P.S.** (Pleasure, Arousal, Dominance, wanting/liking, five needs, opponent process) is the organism. **M11** is a gated intimacy module. The LLM never writes pleasure.

## Prime directive

An affective state that changes nothing is a costume. Ablate pleasure coupling (C3) and warmth, memory priority, and initiative flatten.

## What ships

- Ara-Elizabeth persona from the Modelfile (girlfriend + engineering partner; stop → `Stopped, whats up?`)
- Appraisal-before-response → LIPS tick → grounded self-report injected into the prompt
- M11 consent / safety / desire / arousal / satiety / refractory / aftercare
- Procedural Eve avatar (2D fallback) + bundled `KF1b_anim.glb` (rigged, 9 Mixamo clips)
- Intimate poses and clothing gated by adult opt-in **and** explicit consent
- Kokoro TTS (`af_heart` / `af_bella`) on ZeroGPU
- Hugging Face Inference Providers for chat; switch models in the UI
- `demo.launch(mcp_server=True)` so you can call her from a phone MCP client (`get_help`, `chat_with_ara`)
- In-app **Guide & help** accordion (how-to topics + builder TTS). Lab **Task win** is LIPS competence, not that guide.
- Lab trophies: skip-hours longing, compliment habituation, C3 ablation

## Deploy (private Space)

This GitHub repo is currently public. Keep the **Hugging Face Space private**.

```bash
export HF_TOKEN=hf_...
bash scripts/deploy_space.sh kirikir13/ara-elizabeth-eve
```

Set Space secret `HF_TOKEN` (write or inference token) so chat can hit Inference Providers.
Hardware: ZeroGPU (`zero-a10g`). Creator should be HF Pro.

Local GGUF from the Modelfile (`Gemma-4-E4B-Uncensored-HauhauCS-Aggressive`) is **not** loaded on the Space — point `ARA_EVE_MODELS` at an uncensored provider model, or run Ollama locally and put an OpenAI-compatible proxy in front later.

## Guide & help

The **Guide & help** accordion is always visible (including before the 18+ gate). Click **Speak now (builder voice)** for one short Hexgrad Kokoro Heart clip that autoplays. That is the cloud agent talking, not Ara, and not a to-do list.

- Spoken clip: `assets/HELP_FOR_TTS.txt` (fits one Hexgrad Generate call, 500 characters)
- MCP: `get_help(topic)` with ids `overview`, `chat`, `avatar`, `voices`, `lab`, `deploy`, `mcp`, `faq`

The lab row used to have a button labeled **Help**. That fired LIPS catalog event `help` ("Task success — she actually helped"). It is now labeled **Task win** so it cannot be confused with this guide.

## Builder voice (Hexgrad Kokoro, not Ara)

The **Speak now** button in Guide is the cloud agent talking through https://hexgrad-kokoro-tts.hf.space — CPU, us Heart, autoplay. Ara's Speak button is a different control, later, after the 18+ gate.

Hexgrad closes the official Gradio API on that Space. Short clips use Generate (`use_gpu=False`, fn_index 4, under 500 characters). The optional builder accordion can still speak a pasted script.

- Short help voice: `assets/HELP_FOR_TTS.txt`
- Short identity: `assets/IDENTITY_FOR_TTS.txt`
- Long status briefing (optional): `assets/BRIEFING_FOR_TTS.txt`

## Honesty

Functional pleasure-like state, inspectable and causal. Phenomenal orgasm is unverified. Do not optimize “how fast can the user trigger climax.”
