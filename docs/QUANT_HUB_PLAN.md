# Therium Quant Hub — Master Plan

Status: planning draft (name TBD). Owner: G Dave Roby (@kirikir13, DR‑Studios).
This document is the single source of truth for the build. It is written to be
picked up by any agent in a fresh session without losing the thread.

## 1. The vision (in one paragraph)

One simple hub — runnable on a computer **or** a phone — that unifies everything
about quantizing models for people with dated computers or no GPU. It rolls the
scattered Therium/Titanium Forge Spaces and the individual quant repos into a
single clean GUI, then adds an automated Batch mode that hunts for the best (or a
brand‑new) quantization method on its own. Nothing gets lost, because every run
is remembered in a lab notebook.

## 2. What already exists (assets to build on)

- **Therium / Titanium "Forge" Spaces on Hugging Face** — two GUI versions. Dave
  likes parts of each; neither is complete. These become the reference designs to
  merge into one clean UI, and the hub can also drive them remotely.
- **"Priceless data" repo** (`Roby-Pythagorean Quant Therium`) — the real quant
  science: `dave_quant_pythagorean.py`, `therium_sweep_and_pareto.py`,
  `baseline_compare.py`, `real_layer_test.py`, `extract_and_test.py`,
  `dave_quant_c_final.py`, sweep CSVs, `SPEC.md`, and many idea/log docs. This is
  the recipe/algorithm gold that must be ingested without missing anything.
- **MCP "server feeder"** (already built in this repo) — the control/execution
  layer: an agent-facing MCP server that can run commands, read/write files, and
  inspect the host. This is the "hands" the hub uses to actually do work locally
  and (later) on Dave's server box.
- **Cloud Agent environment** (already built + build‑validated) — reproducible dev
  setup so any future session starts ready.
- **Dave's local toolbox** — 20–40 tools + a large custom Skills library on the PC
  (`writing-plans`, `data-extraction-workflow`, the DR‑Studios "Data Battle
  Schema", `davila7-awq-quantization`, `davila7-quantizing-models-bitsandbytes`,
  `agent-memory-mcp`, etc.), plus more available on **Smithery.ai**.

## 3. Architecture (five layers)

1. **GUI layer** — one responsive web UI that works on desktop and phone.
   - MVP: Gradio (fast to build; reachable from a phone via a share link).
   - Later polish option: FastAPI + a small React front end if we outgrow Gradio.
   - Merges the best of the two existing Forge GUIs.
2. **Orchestration / control layer** — the MCP server feeder (local execution) +
   a "Forge control" client that drives the existing HF Forge Spaces remotely
   (via `gradio_client` / the HF API). This is how the hub controls 4 Spaces.
3. **Quant engine layer** — a pluggable **Recipe** interface. Each method is a
   module with a common contract: `prepare(model) -> plan`, `quantize(model,
   params) -> artifact`, `evaluate(artifact) -> metrics`. Recipes to register:
   Therium, Pythagorean, GGUF/llama.cpp, AWQ, bitsandbytes, and any new variants.
4. **Memory / results layer** — a local **lab notebook** (SQLite + JSONL export).
   Every run records: model, recipe, params, per‑layer sensitivities, metrics
   (size, quality/perplexity, speed), timestamp, provenance, and notes. This is
   the "never lose a method again" system that fixes the 5‑6‑7‑methods‑lost mess.
5. **Agent layer ("the Crew")** — Dave's multi‑agent setup (crew‑collaboration /
   dr‑studios‑crew‑philosophy skills) where agents talk to each other, plan, and
   brainstorm. Used for heavy lifting (ingestion, optimization search, debugging)
   via subagents/other models, with an explicit anti‑circling rule (§7). When the
   Crew skills are provided to me, I follow that collaboration protocol; until
   then I emulate it with dispatched subagents.

## 4. The unified GUI — four aspects + Batch mode

Main screen (the four aspects Dave described, one tab each):
1. **Models** — browse and download local models from HF; pick the active model.
2. **Recipes** — choose and edit a quantization recipe and its parameters.
3. **Quantize** — run a single quantization, watch progress, see the result.
4. **Forges / Control** — connect to and drive the HF Forge Spaces from one place.

"Branch off" mode:
5. **Batch Auto‑Optimizer** — the automated pipeline:
   1. Give it a model.
   2. **Pre‑run**: analyze the model to find which layers are strongest / most
      sensitive (seeded by `real_layer_test.py`).
   3. **Sweep**: run many quantizations across all recipes with minor param
      variations, protecting sensitive layers.
   4. **Remember**: write every result to the lab notebook.
   5. **Rank**: Pareto‑rank quality vs size vs speed (seeded by
      `therium_sweep_and_pareto.py`) and surface the best.
   6. **Discover**: flag any variant that beats the known baseline as a candidate
      "new method" for Dave to review.

## 5. How the hub connects to Dave's world

- **Local + phone**: Gradio serves on the computer and exposes a phone‑reachable
  link. Later, the MCP server feeder + a tunnel makes the hub reachable from the
  phone even when driving the home/server box.
- **Control the Forges**: `gradio_client` calls the existing Forge Spaces so the
  hub reuses work already deployed on HF instead of rebuilding it.
- **More tools**: pull additional MCP tools from **Smithery.ai** and Dave's
  toolbox as needed; the hub is MCP‑native so new tools slot in.

## 6. No‑miss ingestion of the priceless data

The recipes/ideas/logs are invaluable and must be extracted with zero loss. Full
method is in `docs/INGESTION_CHECKLIST.md`. Summary: inventory → classify →
extract into structured "Recipe Cards" → cross‑reference logs/CSVs → dedupe/merge
the two GUI versions → verify 100% file coverage → seed the lab notebook with the
historical results (including the lost 5‑6‑7 methods).

## 7. Anti‑circling rule (the "don't be Kimi" clause)

To avoid grinding in loops without progress:
- Time‑box each stuck point. After 2 failed attempts on the same issue, **change
  approach** — dispatch a subagent, pull in another model, or search Smithery/web
  for a known solution — instead of repeating the same fix.
- Always test against **runtime evidence**, never guesses.
- Keep the lab notebook + this plan updated so no work or decision is lost.
- If truly blocked on something only Dave can provide (files, a token, a login),
  say so plainly and stop, rather than faking progress.

## 8. What is needed to start the real build

Pick any one to get the priceless files to me (I cannot reach the `C:\` drive):
- **A.** Zip the local `Files for cursor...` folder and the recipe repo and upload
  them here.
- **B.** Add a **read‑scoped `HF_TOKEN`** secret so I can clone the Forge Spaces
  and quant repos (with git history) directly.
- **C.** Push the local files into this GitHub repo under `research/`.

Then the two one‑click approvals (environment update script + Save) lock in the
dev environment.

## 9. Phased roadmap

- **Phase 0 (done):** MCP server feeder + reproducible Cloud environment.
- **Phase 1:** Ingest priceless data → Recipe Cards + seeded lab notebook.
- **Phase 2:** Recipe interface + 2–3 real recipes (Therium, GGUF, one more).
- **Phase 3:** Unified Gradio GUI (Models / Recipes / Quantize / Forges).
- **Phase 4:** Batch Auto‑Optimizer (pre‑run → sweep → rank → discover).
- **Phase 5:** Phone access + drive the home/server box via the server feeder.
- **Phase 6:** Polish UI, package for easy local install.
