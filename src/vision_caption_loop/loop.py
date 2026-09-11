"""Caption → verify → refine once when the draft misses a must-tag."""

from __future__ import annotations

from dataclasses import dataclass

from vision_caption_loop.caption import Captioner
from vision_caption_loop.scenes import Scene
from vision_caption_loop.verify import Verdict, verify_caption


@dataclass(frozen=True)
class LoopResult:
    scene: Scene
    draft: str
    draft_verdict: Verdict
    final: str
    final_verdict: Verdict
    refined: bool


def run_loop(scene: Scene, captioner: Captioner) -> LoopResult:
    draft = captioner.caption(scene, draft=None)
    draft_verdict = verify_caption(scene, draft)
    if draft_verdict.ok:
        return LoopResult(
            scene=scene,
            draft=draft,
            draft_verdict=draft_verdict,
            final=draft,
            final_verdict=draft_verdict,
            refined=False,
        )
    final = captioner.caption(scene, draft=draft)
    final_verdict = verify_caption(scene, final)
    return LoopResult(
        scene=scene,
        draft=draft,
        draft_verdict=draft_verdict,
        final=final,
        final_verdict=final_verdict,
        refined=True,
    )
