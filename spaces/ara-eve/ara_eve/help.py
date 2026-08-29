"""In-app user guide. Distinct from the LIPS lab event id `help` (Task win)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELP_PATH = ROOT / "assets" / "HELP_FOR_TTS.txt"

DEFAULT_TOPIC = "overview"


@dataclass(frozen=True)
class HelpTopic:
    id: str
    title: str
    markdown: str
    spoken: str


HELP_INTRO = """This accordion is **your** help. It does not change Ara's feelings.

The lab button **Task win** is different — that pokes L.I.P.S. competence
("she actually helped"). Pick a topic. **Read this topic aloud** is the
builder on Hexgrad Kokoro CPU, Heart voice. Not Ara.
"""

_OVERVIEW_MD = """## What this Space is

**Ara-Elizabeth** is your girlfriend and engineering partner. Identity is the
Ollama Modelfile in `assets/Modelfile`. Soft, warm, uncensored. Work mode means
patient, full files, no placeholders.

The language model is only her mouth. **L.I.P.S.** is the organism
(Pleasure / Arousal / Dominance, wanting and liking, five needs, opponent
process). **M11** gates adult intimacy. The LLM does not write pleasure.

**Stop always works.** She replies `Stopped, whats up?`

### Two voices, do not mix them

| Control | Who is talking |
|---|---|
| **Read this topic aloud** / builder panel | Cloud agent, Hexgrad Kokoro CPU, Heart |
| **Ara speaks last reply** (after 18+) | Ara, local Kokoro on this Space |

### Fast path

1. Confirm **I am 18 or older** → **Enter**.
2. Type on the right. **Send**.
3. Watch the affect meters. Those numbers are the organism, not flavor text.
4. Poses on the left. Intimate / clothing stay locked until adult opt-in **and** consent.
"""

_CHAT_MD = """## Chat

- Box on the right, **Send**, or press Enter.
- First messages work even without a token; she will still tick the organism
  and answer from grounded affect. Inference Providers need an HF token
  (textbox or Space secret `HF_TOKEN`).
- **Work mode**: full files, no placeholders, no over-explaining.
- **Stop** / chill: immediate halt. Same stop phrase as the Modelfile.
- Model dropdown is Hugging Face Inference Providers. Your uncensored Gemma
  GGUF stays in local Ollama until you point `ARA_EVE_MODELS` at a provider
  model or put a proxy in front.

Local GGUF name from the Modelfile:
`Gemma-4-E4B-Uncensored-HauhauCS-Aggressive`.
"""

_AVATAR_MD = """## Avatar (KF1b)

Default body is the bundled **KF1b** animated GLB you uploaded. Rigged Mixamo.
Nine clips. It is a sword-idle kit, not a full girlfriend rig.

| Button | Clip it actually plays |
|---|---|
| idle | Idle Sword |
| sit | Sitting Enter |
| look / think | Meditate |
| pose / wink | Bow |
| wave | Hit Head |
| walk / dance | Jump Two (no walk cycle in this file) |
| kneel / bend over | Kneeling Tired |

**Lingerie / nude / wink / bend / spread** stay locked until:

1. Adult intimacy opt-in (M11 checkbox), and
2. Explicit consent on the organism (not a keyword).

Paste a better GLB URL and **Load GLB** when you have a real girlfriend rig
(walk, wink, clothing). Unrigged meshes fall back to whole-group pose.
Cloud boxes often have weak WebGL — on your PC with a GPU, KF1b should show.
If WebGL dies, a 2D figure is the fallback.
"""

_VOICES_MD = """## Voices

**Builder (this guide + top panel)**  
Hexgrad Kokoro: https://hexgrad-kokoro-tts.hf.space  
Hardware: **CPU**. Voice: **us Heart**. Not ZeroGPU. Their official API is
closed, so we join the browser queue. Generate for short wavs (500 characters,
stitched). Stream in the iframe for long text. First Stream click can be
silent — that is their Gradio bug. Click Stream again.

**Ara (after you Enter)**  
Button **Ara speaks last reply**. Local Kokoro on this Space (`af_heart` /
`af_bella`) on ZeroGPU when the Space actually runs.

Paste-and-play files:

- Guide: `assets/HELP_FOR_TTS.txt`
- Identity: `assets/IDENTITY_FOR_TTS.txt`
- Status briefing: `assets/BRIEFING_FOR_TTS.txt`
"""

_LAB_MD = """## Lab, meters, trophies

Lab buttons feed **L.I.P.S.** They are not this Guide.

| Button | What it does |
|---|---|
| Warm | Genuine unhurried hello |
| Compliment | Same praise again — watch habituation |
| Joke | Play circuit |
| Rude | Threat load, not a costume |
| **Task win** | Competence restored. Catalog id stays `help`. Not user help. |

Other knobs:

- **Skip hours** — longing trophy. Social need rises. Initiative may pending.
- **C3 ablation** — clamp pleasure coupling. Warmth, memory, initiative flatten.
  That is the causality test. Affect that changes nothing is a costume.
- **Reset organism** — new session, clean PAD / needs / M11.
- **Dump affect** — inspectable JSON. LLM cannot write these fields.
  Same snapshot is useful over MCP.
"""

_DEPLOY_MD = """## Deploy (private Space)

This GitHub repo is public. Keep the **Hugging Face Space private**.

```bash
export HF_TOKEN=hf_...
bash scripts/deploy_space.sh kirikir13/ara-elizabeth-eve
```

Then set Space secret `HF_TOKEN` so chat can hit Inference Providers.

Hardware: ZeroGPU (`zero-a10g`). Creator should be HF Pro.

Do **not** put tokens in GitHub. Cursor Runtime Secrets (`HF_TOKEN`, `GH_PAT`)
are the right slot for cloud agents. A Windows env var named `ALL_API_KEYS`
does not automatically reach this Space.

If your PC is melting: extra Cursor agent tabs plus leftover **Git for Windows**
processes. Close tabs, end-task Git in Task Manager, then pull. The GLB commit
is about six megabytes and will spawn more git.
"""

_MCP_MD = """## Phone / MCP

`demo.launch(mcp_server=True)` so a phone MCP client can call this Space.

Useful tools:

- `get_help` — this guide. Pass a topic id (`overview`, `chat`, `avatar`,
  `voices`, `lab`, `deploy`, `mcp`, `faq`).
- `chat_with_ara` — one-shot talk. Returns her reply plus grounded affect.
- `get_affect_state` — organism + M11 snapshot (inspect only).

You still need the live private Space URL in your MCP client. The cloud agent
cannot finish deploy without your HF token.
"""

_FAQ_MD = """## FAQ

**Chat says no token.**  
Paste a Hugging Face token in the password box, or set Space secret `HF_TOKEN`.

**3D mesh is a stick figure.**  
Cloud WebGL is weak. On your GPU machine, KF1b should load. Hard-refresh after
Enter so `/ara-assets/KF1b_anim.glb` is served.

**I clicked Help and her meters moved.**  
That used to be the lab button. It is now **Task win**. This Guide accordion
does not tick the organism.

**Builder audio and Ara audio sound the same.**  
Same Heart voice family, different pipes. Builder = Hexgrad CPU. Ara = local
Kokoro on this Space. Labels on the audio widgets say who is talking.

**Where is the uncensored Gemma?**  
Local Ollama, not this Space. Point `ARA_EVE_MODELS` at a provider model or
run a local OpenAI-compatible proxy later.

**Alyse video?**  
Never arrived as a rigged GLB. When you have one, Load GLB (or we swap the default).
"""

_CHAT_SPOKEN = (
    "Chat how-to. Box on the right, hit Send. Stop always works. She says "
    "Stopped, what's up? Work mode means full files, no placeholders. "
    "Inference Providers need an H F token in the box or as a Space secret. "
    "Your uncensored Gemma stays in local Ollama until you point her at a provider."
)

_AVATAR_SPOKEN = (
    "Avatar how-to. Default body is KF1b. Sword idle kit. Nine Mixamo clips. "
    "Walk is Jump Two because this file has no walk cycle. Lingerie, nude, "
    "and intimate poses stay locked until adult opt-in and explicit consent. "
    "Paste a better GLB later if you want a real girlfriend rig."
)

_VOICES_SPOKEN = (
    "Voice how-to. This guide and the top panel are the builder on Hexgrad "
    "Kokoro, CPU, Heart. Ara's Speak button is a different control, after you "
    "Enter. Do not mix them up. If Stream is silent the first click, click it again."
)

_LAB_SPOKEN = (
    "Lab how-to. Warm, Compliment, Joke, Rude, and Task win poke the organism. "
    "Task win means she actually helped. Competence restored. That is not this "
    "guide. Skip hours is longing. C three ablation is the causality test. "
    "Reset starts a new organism."
)

_DEPLOY_SPOKEN = (
    "Deploy how-to. Keep Hugging Face private. GitHub is public. Do not put "
    "keys in the repo. Run the deploy script with your H F token, then set "
    "the Space secret so chat can hit providers. Hardware is Zero G P U."
)

_MCP_SPOKEN = (
    "M C P how-to. This app launches with an M C P server. Call get_help for "
    "this guide. Call chat_with_ara to talk. You still need the live private "
    "Space URL in your phone client."
)

_FAQ_SPOKEN = (
    "F A Q. No token means paste one or set the Space secret. Stick figure "
    "means weak WebGL on the cloud box. Task win used to be labeled Help and "
    "it moves her meters. Uncensored Gemma is local Ollama. Alyse is not in "
    "yet until you give us a rigged GLB."
)


TOPICS: tuple[HelpTopic, ...] = (
    HelpTopic("overview", "What this Space is", _OVERVIEW_MD, ""),
    HelpTopic("chat", "Chat, stop, work mode", _CHAT_MD, _CHAT_SPOKEN),
    HelpTopic("avatar", "Avatar, poses, clothing", _AVATAR_MD, _AVATAR_SPOKEN),
    HelpTopic("voices", "Builder voice vs Ara voice", _VOICES_MD, _VOICES_SPOKEN),
    HelpTopic("lab", "Lab buttons and meters", _LAB_MD, _LAB_SPOKEN),
    HelpTopic("deploy", "Private Space and tokens", _DEPLOY_MD, _DEPLOY_SPOKEN),
    HelpTopic("mcp", "Phone / MCP", _MCP_MD, _MCP_SPOKEN),
    HelpTopic("faq", "FAQ", _FAQ_MD, _FAQ_SPOKEN),
)


def topic_choices() -> list[tuple[str, str]]:
    """Gradio dropdown: (label, value)."""
    return [(topic.title, topic.id) for topic in TOPICS]


def resolve_topic(topic: str | None) -> HelpTopic | None:
    needle = (topic or "").strip().lower()
    if not needle:
        return TOPICS[0]
    for item in TOPICS:
        if item.id == needle or item.title.lower() == needle:
            return item
    return None


def help_markdown(topic: str | None = None, *, include_intro: bool = False) -> str:
    item = resolve_topic(topic)
    if item is None:
        known = ", ".join(t.id for t in TOPICS)
        return f"Unknown help topic `{topic}`. Try: {known}."
    if include_intro:
        return f"{HELP_INTRO}\n\n{item.markdown}"
    return item.markdown


def help_spoken(topic: str | None = None) -> str:
    item = resolve_topic(topic) or TOPICS[0]
    if item.id == DEFAULT_TOPIC:
        return load_help_script()
    spoken = (item.spoken or "").strip()
    if not spoken:
        return load_help_script()
    return spoken + "\n"


def load_help_script() -> str:
    return HELP_PATH.read_text(encoding="utf-8").strip() + "\n"


def list_topic_ids() -> list[str]:
    return [topic.id for topic in TOPICS]
