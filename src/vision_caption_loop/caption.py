"""Captioners: deterministic mock (tests) + optional live OpenAI vision."""

from __future__ import annotations

import os
from typing import Protocol

from vision_caption_loop.scenes import Scene


class Captioner(Protocol):
    def caption(self, scene: Scene, *, draft: str | None = None) -> str: ...


class MockCaptioner:
    """Deterministic captions from scene tags — no network, no secrets.

    Pass 1 (draft is None): a vague caption that deliberately omits the last
    must-tag (replaced with "shop part"). Cues are not quoted in the draft so
    they cannot leak the missing tag into the verify step.

    Pass 2 (draft set): a refined caption that names every must-tag plus cues.
    That gap is the whole teaching point of the loop.
    """

    def caption(self, scene: Scene, *, draft: str | None = None) -> str:
        if draft is None:
            soft = list(scene.must_tags[:-1]) + ["shop part"]
            return (
                f"A shop photo shows a {', '.join(soft)} "
                f"in a typical garage setup."
            )
        tags = ", ".join(scene.must_tags)
        cue2 = scene.cues[1] if len(scene.cues) > 1 else scene.cues[0]
        return (
            f"Close-up of {tags}: {scene.cues[0]}, with {cue2} visible. "
            f"Draft was incomplete; refined to name the parts."
        )


class OpenAICaptioner:
    """Optional live vision caption via OpenAI — never used by tests."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY required for --live")

    def caption(self, scene: Scene, *, draft: str | None = None) -> str:
        import httpx

        # Live path still works off the scene's cue text (no real image bytes in
        # this teaching repo). Real vision would attach an image URL / base64.
        prompt = (
            "Write one short factual caption for a shop-maintenance photo. "
            f"Visible cues: {', '.join(scene.cues)}. "
            f"Must mention these parts if present: {', '.join(scene.must_tags)}."
        )
        if draft:
            prompt += f" Improve this draft caption: {draft!r}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "max_tokens": 120,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
