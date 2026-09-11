"""CLI: python -m vision_caption_loop --mock [--json] [--scene ...]"""

from __future__ import annotations

import argparse
import json
import sys

from vision_caption_loop.caption import MockCaptioner, OpenAICaptioner
from vision_caption_loop.loop import run_loop
from vision_caption_loop.scenes import DEFAULT_SCENE_ID, SCENE_BANK, get_scene


def _format_text(result, mode: str) -> str:
    scene = result.scene
    lines: list[str] = []
    lines.append(f"[{mode}] vision caption loop — scene: {scene.id}")
    lines.append(f"cues: {', '.join(scene.cues)}")
    lines.append(f"must_tags: {', '.join(scene.must_tags)}")
    lines.append("")
    lines.append(f"draft:  {result.draft}")
    lines.append(
        f"verify: score={result.draft_verdict.score:.2f} "
        f"hit={list(result.draft_verdict.hit)} miss={list(result.draft_verdict.miss)} "
        f"ok={result.draft_verdict.ok}"
    )
    if result.refined:
        lines.append("")
        lines.append(f"refine: {result.final}")
        lines.append(
            f"verify: score={result.final_verdict.score:.2f} "
            f"hit={list(result.final_verdict.hit)} miss={list(result.final_verdict.miss)} "
            f"ok={result.final_verdict.ok}"
        )
    else:
        lines.append("(draft already complete — no refine pass)")
    lines.append("")
    status = "PASS" if result.final_verdict.ok else "FAIL"
    lines.append(f"[{mode}] {status} — final caption names all must-tags.")
    lines.append(f"Shop note: {scene.shop_note}")
    return "\n".join(lines)


def _format_json(result, mode: str) -> str:
    payload = {
        "mode": mode,
        "scene": result.scene.id,
        "cues": list(result.scene.cues),
        "must_tags": list(result.scene.must_tags),
        "draft": result.draft,
        "draft_verdict": {
            "ok": result.draft_verdict.ok,
            "score": round(result.draft_verdict.score, 4),
            "hit": list(result.draft_verdict.hit),
            "miss": list(result.draft_verdict.miss),
        },
        "refined": result.refined,
        "final": result.final,
        "final_verdict": {
            "ok": result.final_verdict.ok,
            "score": round(result.final_verdict.score, 4),
            "hit": list(result.final_verdict.hit),
            "miss": list(result.final_verdict.miss),
        },
        "shop_note": result.scene.shop_note,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def build_parser() -> argparse.ArgumentParser:
    known = ", ".join(s.id for s in SCENE_BANK)
    p = argparse.ArgumentParser(
        prog="vision_caption_loop",
        description="Day-7: caption → verify → refine on mock shop scenes.",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use deterministic mock captions (default).",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="Call OpenAI chat API (needs OPENAI_API_KEY).",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    p.add_argument(
        "--scene",
        default=DEFAULT_SCENE_ID,
        help=f"Scene id (default: {DEFAULT_SCENE_ID!r}). Known: {known}.",
    )
    p.add_argument(
        "--list-scenes",
        action="store_true",
        help="Print scene ids and exit.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list_scenes:
        for scene in SCENE_BANK:
            print(f"{scene.id}\t{', '.join(scene.must_tags)}")
        return 0

    try:
        scene = get_scene(args.scene)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.live:
        captioner = OpenAICaptioner()
        mode = "live"
    else:
        captioner = MockCaptioner()
        mode = "mock"

    result = run_loop(scene, captioner)
    if args.json:
        print(_format_json(result, mode))
    else:
        print(_format_text(result, mode))
    return 0 if result.final_verdict.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
