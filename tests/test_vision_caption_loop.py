"""Tests for vision-caption-loop — mock path only, no network."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from vision_caption_loop.caption import MockCaptioner
from vision_caption_loop.loop import run_loop
from vision_caption_loop.scenes import DEFAULT_SCENE_ID, SCENE_BANK, get_scene
from vision_caption_loop.verify import verify_caption


def test_scene_bank_nonempty_and_unique_ids():
    assert len(SCENE_BANK) >= 4
    ids = [s.id for s in SCENE_BANK]
    assert len(ids) == len(set(ids))


def test_get_scene_default():
    scene = get_scene(DEFAULT_SCENE_ID)
    assert scene.id == "brake_pads"
    assert "brake" in scene.must_tags


def test_get_scene_unknown_raises():
    with pytest.raises(KeyError, match="unknown scene"):
        get_scene("not_a_real_scene")


def test_mock_draft_misses_last_tag():
    scene = get_scene("brake_pads")
    draft = MockCaptioner().caption(scene, draft=None)
    verdict = verify_caption(scene, draft)
    assert verdict.ok is False
    assert scene.must_tags[-1] in verdict.miss
    assert verdict.score < 1.0


def test_mock_refine_hits_all_tags():
    scene = get_scene("brake_pads")
    cap = MockCaptioner()
    draft = cap.caption(scene, draft=None)
    final = cap.caption(scene, draft=draft)
    verdict = verify_caption(scene, final)
    assert verdict.ok is True
    assert verdict.miss == ()
    assert set(verdict.hit) == set(scene.must_tags)
    assert abs(verdict.score - 1.0) < 1e-9


def test_verify_case_insensitive():
    scene = get_scene("breaker_panel")
    caption = "OPEN BREAKER PANEL with a TRIPPED handle"
    verdict = verify_caption(scene, caption)
    assert verdict.ok is True


def test_verify_partial_score():
    scene = get_scene("radiator_hose")
    # only two of three must-tags
    caption = "A radiator hose is swollen"
    verdict = verify_caption(scene, caption)
    assert verdict.ok is False
    assert "clamp" in verdict.miss
    assert abs(verdict.score - (2 / 3)) < 1e-9


def test_run_loop_refines_default_scene():
    scene = get_scene(DEFAULT_SCENE_ID)
    result = run_loop(scene, MockCaptioner())
    assert result.refined is True
    assert result.draft_verdict.ok is False
    assert result.final_verdict.ok is True
    assert result.final_verdict.miss == ()


def test_run_loop_all_scenes_pass_after_refine():
    cap = MockCaptioner()
    for scene in SCENE_BANK:
        result = run_loop(scene, cap)
        assert result.final_verdict.ok, f"{scene.id} failed: {result.final_verdict}"
        assert result.refined is True  # mock draft always leaves one miss


def test_cli_mock_default_exit_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "vision_caption_loop", "--mock"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "brake_pads" in proc.stdout
    assert "PASS" in proc.stdout
    assert "refine:" in proc.stdout


def test_cli_json_shape():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "vision_caption_loop",
            "--mock",
            "--json",
            "--scene",
            "kitchen_drain",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["scene"] == "kitchen_drain"
    assert data["mode"] == "mock"
    assert data["refined"] is True
    assert data["final_verdict"]["ok"] is True
    assert data["draft_verdict"]["ok"] is False
    assert sorted(data["must_tags"]) == sorted(["drain", "sink", "p-trap"])


def test_cli_list_scenes():
    proc = subprocess.run(
        [sys.executable, "-m", "vision_caption_loop", "--list-scenes"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    for scene in SCENE_BANK:
        assert scene.id in proc.stdout


def test_cli_unknown_scene_exits_2():
    proc = subprocess.run(
        [sys.executable, "-m", "vision_caption_loop", "--mock", "--scene", "nope"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
