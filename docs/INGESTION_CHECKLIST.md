# No‑Miss Ingestion Checklist — Priceless Quant Data

Goal: pull every valuable idea, recipe, and result out of Dave's files with zero
loss, and turn it into structured, reusable assets for the hub. This exists
because methods have been lost before (the "5‑6‑7 quantization methods" mess).
It mirrors Dave's own `data-extraction-workflow` / "Data Battle Schema" approach.

## Inputs expected

- The `Roby-Pythagorean Quant Therium` repo (recipes, scripts, CSVs, docs).
- The local `Files for cursor... local central hub and GUI` folder (incl. F_GUI
  and the two Forge GUI versions).
- Any project master zips: `Project_Dave_Quant_Master.zip`,
  `Dave_Quant_Project_Master_Log(raw).zip`, and session/debrief logs.

## Step 1 — Inventory (prove we have everything)

- Build a manifest of every file: path, type, size, SHA‑256 hash.
- Expand every `.zip`/`.docx` and manifest their contents too (no black boxes).
- Record the manifest in `research/manifest.csv`. Nothing proceeds until every
  file appears here.

## Step 2 — Classify

Tag each file into one or more buckets:
- **Recipe / algorithm** (the quant methods and math).
- **Experiment log** (session notes, "thoughts", debriefs).
- **Results / data** (CSVs, sweeps, pareto plots, baselines).
- **GUI / app code** (the two Forge GUIs, F_GUI, vite/TS app).
- **Ideas / concepts** (RotorQuant, TurboQuant, Topological Flat Transformers…).
- **Config / infra** (`.env.example`, package files, SPEC.md).

## Step 3 — Extract into Recipe Cards

For every recipe/algorithm, produce a structured card in `research/recipes/`:
- Name + aliases; one‑line summary.
- The method: math/approach in plain terms + key formulas.
- Parameters and their ranges/defaults.
- Provenance: source file(s) + hash.
- Known results: any metrics found (size, quality, speed) and where.
- Status: proven / partial / idea‑only.
- Open questions / what was "needing some stuff" when last left off.

## Step 4 — Cross‑reference logs and results

- Link each CSV/plot to the recipe(s) it tested.
- Reconstruct the timeline of experiments from the logs.
- Explicitly recover the lost 5‑6‑7 methods: find every mention, gather their
  params/results, and give each its own Recipe Card so they are never lost again.

## Step 5 — Dedupe, reconcile, merge

- Two Forge GUI versions → one feature matrix; mark the best parts of each to
  merge into the unified UI.
- Multiple variants of the same recipe → one card with a version history.
- Flag contradictions between docs for Dave to resolve (do not silently pick).

## Step 6 — Verify 100% coverage

- Every file in `research/manifest.csv` must be marked reviewed, with a pointer
  to what it produced (a card, a note, or "not relevant — reason").
- A coverage report lists anything ambiguous or skipped for Dave's sign‑off.
- Use parallel subagents ("the Crew") for volume; each returns cards, then one
  synthesis pass reconciles them. No single file is left unread.

## Step 7 — Seed the system

- Import all recovered historical results into the lab‑notebook memory DB so the
  Batch Auto‑Optimizer starts from prior knowledge, not a blank slate.
- Register every proven/partial recipe in the engine's recipe registry.

## Output

- `research/manifest.csv` — full file inventory with hashes + review status.
- `research/recipes/*.md` — one Recipe Card per method.
- `research/coverage_report.md` — proof nothing was missed + items for review.
- Seeded lab‑notebook DB + populated recipe registry.
