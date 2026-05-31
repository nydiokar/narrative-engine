"""Soft Gate — quality ranking among sound narrative candidates.

Candidates that pass the hard gate are scored on these dimensions:
- Genre Fit (high weight)
- Thematic Clarity (high weight)
- Conflict Density (medium weight)
- Relationship Tension (medium weight)
- Scene-Level Purpose (high weight)
- Suspense/Curiosity/Surprise (medium weight)
- Emotional Transport (medium weight)
- Novelty (high weight)
- Prose Distinctiveness (low weight)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SoftGateDimension:
    name: str
    description: str
    weight: str  # high, medium, low
    score: int = 0  # 0-10
    notes: str = ""


@dataclass
class SoftGateResult:
    passed: bool = False
    dimensions: list[SoftGateDimension] = field(default_factory=list)
    composite_score: float = 0.0
    threshold: float = 0.0
    notes: list[str] = field(default_factory=list)


WEIGHT_MAP: dict[str, float] = {
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
}


DIMENSION_DEFS: list[SoftGateDimension] = [
    SoftGateDimension(name="genre_fit", description="Does the artifact deliver on genre promises?", weight="high"),
    SoftGateDimension(name="thematic_clarity", description="Are the declared themes instantiated in the fabula?", weight="high"),
    SoftGateDimension(name="conflict_density", description="How many conflict types are active? How layered?", weight="medium"),
    SoftGateDimension(name="relationship_tension", description="Are character relationships under productive pressure?", weight="medium"),
    SoftGateDimension(name="scene_level_purpose", description="Does every scene pass the 5-question Greimas diagnostic?", weight="high"),
    SoftGateDimension(name="suspense_curiosity_surprise", description="Does narrative manage reader attention through information control?", weight="medium"),
    SoftGateDimension(name="emotional_transport", description="Does the emotional arc engage and sustain reader involvement?", weight="medium"),
    SoftGateDimension(name="novelty", description="Is the candidate a low-similarity recombination within its genre band?", weight="high"),
    SoftGateDimension(name="prose_distinctiveness", description="Does the style have identifiable voice and texture?", weight="low"),
]


class SoftGate:
    """Evaluates quality dimensions of a narrative candidate."""

    def __init__(self, threshold: float = 5.0) -> None:
        self.threshold = threshold
        self.dimensions: list[SoftGateDimension] = [
            SoftGateDimension(**d.__dict__) for d in DIMENSION_DEFS
        ]

    def set_score(self, dimension_name: str, score: int, notes: str = "") -> None:
        for dim in self.dimensions:
            if dim.name == dimension_name:
                if 0 <= score <= 10:
                    dim.score = score
                if notes:
                    dim.notes = notes
                return
        msg = f"Unknown dimension: {dimension_name}"
        raise ValueError(msg)

    def compute_composite(self) -> float:
        total_weighted = 0.0
        total_weight = 0.0
        for dim in self.dimensions:
            w = WEIGHT_MAP.get(dim.weight, 1.0)
            total_weighted += dim.score * w
            total_weight += w
        return total_weighted / total_weight if total_weight > 0 else 0.0

    def evaluate(self) -> SoftGateResult:
        composite = self.compute_composite()
        notes: list[str] = []
        for dim in self.dimensions:
            if dim.score < 4:
                notes.append(
                    f"Low score on '{dim.name}' ({dim.score}/10): {dim.description}"
                )

        return SoftGateResult(
            passed=composite >= self.threshold,
            dimensions=[SoftGateDimension(**d.__dict__) for d in self.dimensions],
            composite_score=composite,
            threshold=self.threshold,
            notes=notes,
        )
