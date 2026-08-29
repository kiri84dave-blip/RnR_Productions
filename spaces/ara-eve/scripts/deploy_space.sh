#!/usr/bin/env bash
# Create (if needed) and push this Space directory to a PRIVATE Hugging Face Space.
# Usage: HF_TOKEN=hf_... bash scripts/deploy_space.sh kirikir13/ara-elizabeth-eve
set -euo pipefail

SPACE_ID="${1:-kirikir13/ara-elizabeth-eve}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "Set HF_TOKEN first: https://huggingface.co/settings/tokens"
  exit 1
fi

if ! command -v hf >/dev/null 2>&1; then
  python3 -m pip install -U huggingface_hub
fi

hf repos create "$SPACE_ID" --type space --space-sdk gradio --flavor zero-a10g --private --exist-ok
hf upload "$SPACE_ID" "$ROOT" . --repo-type space
echo "Pushed to https://huggingface.co/spaces/${SPACE_ID}"
echo "Then: hf spaces secrets set ${SPACE_ID} HF_TOKEN=\$HF_TOKEN"
echo "Hardware is ZeroGPU via --flavor zero-a10g (README hardware: key is ignored)."
