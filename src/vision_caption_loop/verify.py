"""Verify a caption against the scene's must-tags."""

from __future__ import annotations

import re
from dataclasses import dataclass

from vision_caption_loop.scenes import Scene


@dataclass(frozen=True)
class Verdict:
    ok: bool
    score: float
    hit: tuple[str, ...]
    miss: tuple[str, ...]
    caption: str


_WORD = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.I)


def _tokens(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD.finditer(text)}


def verify_caption(scene: Scene, caption: str) -> Verdict:
    """Score = fraction of must_tags present as whole tokens (case-insensitive)."""
    toks = _tokens(caption)
    hit: list[str] = []
    miss: list[str] = []
    for tag in scene.must_tags:
        # allow simple stems: pads→pad, brakes→brake already handled by tag choice
        if tag.lower() in toks:
            hit.append(tag)
        else:
            miss.append(tag)
    total = len(scene.must_tags)
    score = (len(hit) / total) if total else 1.0
    return Verdict(
        ok=len(miss) == 0,
        score=score,
        hit=tuple(hit),
        miss=tuple(miss),
        caption=caption,
    )
