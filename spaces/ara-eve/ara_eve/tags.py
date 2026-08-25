"""Avatar action/emotion tags — port of src/lib/tags.ts plus gated intimate poses."""

from __future__ import annotations

import re
from dataclasses import dataclass

ACTIONS = (
    "idle",
    "walk",
    "wave",
    "sit",
    "dance",
    "think",
    "stretch",
    "pose",
    "nod",
    "look",
    "wink",
    "bend_over",
    "spread_legs",
    "kneel",
)
EMOTIONS = ("neutral", "happy", "sad", "excited", "shy", "playful")
INTIMATE_ACTIONS = {"wink", "bend_over", "spread_legs", "kneel"}

ACTION_ALIASES = {
    "idle": "idle",
    "stand": "idle",
    "standing": "idle",
    "walk": "walk",
    "walking": "walk",
    "stroll": "walk",
    "wave": "wave",
    "waving": "wave",
    "greet": "wave",
    "sit": "sit",
    "sitting": "sit",
    "dance": "dance",
    "dancing": "dance",
    "think": "think",
    "thinking": "think",
    "stretch": "stretch",
    "stretching": "stretch",
    "pose": "pose",
    "teasing": "pose",
    "tease": "pose",
    "playful": "pose",
    "nod": "nod",
    "nodding": "nod",
    "look": "look",
    "looking": "look",
    "wink": "wink",
    "winking": "wink",
    "bend": "bend_over",
    "bend_over": "bend_over",
    "bendover": "bend_over",
    "spread": "spread_legs",
    "spread_legs": "spread_legs",
    "kneel": "kneel",
    "kneeling": "kneel",
}

EMOTION_ALIASES = {
    "neutral": "neutral",
    "calm": "neutral",
    "happy": "happy",
    "smile": "happy",
    "smiling": "happy",
    "sad": "sad",
    "down": "sad",
    "excited": "excited",
    "hype": "excited",
    "shy": "shy",
    "blush": "shy",
    "playful": "playful",
    "flirty": "playful",
}

_TAG_RE = re.compile(r"\[(?:action|emotion|mood|clothing)?:\s*([a-zA-Z_]+)\]|\[([a-zA-Z_]+)\]")


@dataclass
class ParsedTags:
    action: str | None
    emotion: str | None
    clothing: str | None
    display: str


def _pick_action(raw: str) -> str | None:
    key = raw.strip().lower()
    if key in ACTIONS:
        return key
    return ACTION_ALIASES.get(key)


def _pick_emotion(raw: str) -> str | None:
    key = raw.strip().lower()
    if key in EMOTIONS:
        return key
    return EMOTION_ALIASES.get(key)


def parse_tags(text: str, *, intimate_ok: bool = False) -> ParsedTags:
    action: str | None = None
    emotion: str | None = None
    clothing: str | None = None

    def _sub(match: re.Match[str]) -> str:
        nonlocal action, emotion, clothing
        token = (match.group(1) or match.group(2) or "").lower()
        whole = match.group(0).lower()
        if "clothing" in whole:
            clothing = token
            return ""
        if whole.startswith("[emotion") or whole.startswith("[mood"):
            picked_emotion = _pick_emotion(token)
            if picked_emotion:
                emotion = picked_emotion
            return ""
        if whole.startswith("[action"):
            picked_action = _pick_action(token)
            if picked_action:
                action = picked_action
            return ""
        picked_emotion = _pick_emotion(token)
        picked_action = _pick_action(token)
        if picked_emotion and token in EMOTIONS:
            emotion = picked_emotion
        elif picked_action:
            action = picked_action
        elif picked_emotion:
            emotion = picked_emotion
        return ""

    tagged = _TAG_RE.sub(_sub, text or "")

    if not action:
        lower = (text or "").lower()
        if re.search(r"\*\s*walk|\bwalks?\b|\bstrolls?\b", lower):
            action = "walk"
        elif re.search(r"\*\s*wave|\bwaves?\b", lower):
            action = "wave"
        elif re.search(r"\*\s*sit|\bsits?\b", lower):
            action = "sit"
        elif re.search(r"\bdanc", lower):
            action = "dance"
        elif re.search(r"\bwink", lower):
            action = "wink"
        elif re.search(r"\bbend over|\bbends over", lower):
            action = "bend_over"

    if not emotion:
        lower = (text or "").lower()
        if re.search(r"\bsmil|\bgrin|\blaugh", lower):
            emotion = "happy"
        elif re.search(r"\bsigh|\bsad|\bquiet", lower):
            emotion = "sad"

    if action in INTIMATE_ACTIONS and not intimate_ok:
        action = "pose" if action else "idle"
    if clothing in {"nude", "naked"} and not intimate_ok:
        clothing = "dressed"

    return ParsedTags(action=action, emotion=emotion, clothing=clothing, display=re.sub(r"\n{3,}", "\n\n", tagged).strip())


def strip_tags(text: str, *, intimate_ok: bool = False) -> str:
    return parse_tags(text, intimate_ok=intimate_ok).display


DIRECTOR = (
    "You control a 3D avatar. At the END of every reply, append exactly two tags on their own line, nothing after them:\n"
    "[action:idle] or [action:walk] or [action:wave] or [action:sit] or [action:dance] or "
    "[action:think] or [action:stretch] or [action:pose] or [action:nod] or [action:look] "
    "or (only if adult intimacy is on) [action:wink] [action:bend_over] [action:spread_legs] [action:kneel]\n"
    "[emotion:neutral] or [emotion:happy] or [emotion:sad] or [emotion:excited] or [emotion:shy] or [emotion:playful]\n"
    "Optional: [clothing:dressed] or [clothing:lingerie] or [clothing:nude] (nude only if adult intimacy is on).\n"
    "Pick the action that matches what your body is doing. Do not mention the tags in spoken dialogue."
)
