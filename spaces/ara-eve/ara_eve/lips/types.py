"""L.I.P.S. organism types. Faithful port of emotion-workspace src/lib/lips/types.ts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal


def clamp(n: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, n))


@dataclass
class Pad:
    p: float
    a: float
    d: float


@dataclass
class Needs:
    social: float
    novelty: float
    coherence: float
    competence: float
    rest: float


@dataclass
class Chemicals:
    dopamine: float
    serotonin: float
    oxytocin: float
    cortisol: float
    endorphin: float
    norepinephrine: float
    acetylcholine: float


@dataclass
class Appraisal:
    warmth: float
    novelty: float
    praiseworthiness: float
    user_valence: float
    social_contact: float
    competence_gain: float
    coherence_gain: float
    threat: float
    label: str
    family: str


@dataclass
class SubscriberEffect:
    module: Literal["memory", "planner", "policy", "avatar", "report", "intimacy"]
    effect: str
    active: bool


@dataclass
class WorkspacePacket:
    id: str
    at: float
    salience: float
    mood: str
    summary: str
    subscribers: list[SubscriberEffect]


@dataclass
class TraceEvent:
    id: str
    at: float
    kind: Literal["appraisal", "decay", "test", "initiative", "broadcast", "intimacy", "climax"]
    title: str
    detail: str
    delta: dict[str, float] | None = None


@dataclass
class CausalityFlags:
    clamp_pleasure: bool = False
    mask_report: bool = False
    freeze_needs: bool = False


BASELINE = Pad(p=0.12, a=0.04, d=0.08)


@dataclass
class OrganismState:
    pad: Pad
    mood: Pad
    wanting: float
    liking: float
    a_state: float
    b_state: float
    needs: Needs
    chemicals: Chemicals
    bond: float
    sim_time: float
    last_meaningful_at: float
    last_peak_at: float
    recent_families: list[str]
    workspace: WorkspacePacket | None
    trace: list[TraceEvent]
    flags: CausalityFlags
    initiative_pending: bool
    last_utterance: str

    def snapshot(self) -> dict:
        return {
            "pad": {"p": self.pad.p, "a": self.pad.a, "d": self.pad.d},
            "mood": {"p": self.mood.p, "a": self.mood.a, "d": self.mood.d},
            "wanting": self.wanting,
            "liking": self.liking,
            "a_state": self.a_state,
            "b_state": self.b_state,
            "needs": self.needs.__dict__.copy(),
            "chemicals": self.chemicals.__dict__.copy(),
            "bond": self.bond,
            "sim_time": self.sim_time,
            "last_meaningful_at": self.last_meaningful_at,
            "last_peak_at": self.last_peak_at,
            "initiative_pending": self.initiative_pending,
            "last_utterance": self.last_utterance,
            "flags": {
                "clamp_pleasure": self.flags.clamp_pleasure,
                "mask_report": self.flags.mask_report,
                "freeze_needs": self.flags.freeze_needs,
            },
            "workspace": None
            if self.workspace is None
            else {
                "id": self.workspace.id,
                "at": self.workspace.at,
                "salience": self.workspace.salience,
                "mood": self.workspace.mood,
                "summary": self.workspace.summary,
                "subscribers": [s.__dict__.copy() for s in self.workspace.subscribers],
            },
        }


def clone_state(state: OrganismState) -> OrganismState:
    return deepcopy(state)


def initial_state() -> OrganismState:
    return OrganismState(
        pad=Pad(p=BASELINE.p, a=BASELINE.a, d=BASELINE.d),
        mood=Pad(p=0.1, a=0.03, d=0.07),
        wanting=0.38,
        liking=0.0,
        a_state=0.0,
        b_state=0.0,
        needs=Needs(social=0.22, novelty=0.28, coherence=0.12, competence=0.18, rest=0.08),
        chemicals=Chemicals(
            dopamine=0.42,
            serotonin=0.55,
            oxytocin=0.58,
            cortisol=0.18,
            endorphin=0.32,
            norepinephrine=0.28,
            acetylcholine=0.4,
        ),
        bond=0.52,
        sim_time=0.0,
        last_meaningful_at=0.0,
        last_peak_at=-1.0,
        recent_families=[],
        workspace=None,
        trace=[],
        flags=CausalityFlags(),
        initiative_pending=False,
        last_utterance="State is at baseline. Nothing has been appraised yet.",
    )


INITIAL_STATE = initial_state
