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
- `demo.launch(mcp_server=True)` so you can call her from a phone MCP client
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

## Honesty

Functional pleasure-like state, inspectable and causal. Phenomenal orgasm is unverified. Do not optimize “how fast can the user trigger climax.”
