# Contributing to vision-caption-loop

Welcome. This repo is a **day-7 teaching vision caption loop** — mock scenes, must-tag verify, one refine pass. Keep that bar in mind.

## Map (fork → PR)

1. **Fork** this repo on GitHub, then clone your fork:
   ```bash
   git clone https://github.com/<you>/vision-caption-loop.git
   cd vision-caption-loop
   ```
2. **Install** in editable mode with test deps:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Prove the wiring** before you change anything:
   ```bash
   pytest
   python -m vision_caption_loop --mock
   ```
   You want all tests green and a `PASS` where the draft misses a tag and the refine fills it. No API key needed.
4. **Branch** for one small change:
   ```bash
   git checkout -b my-first-pr
   ```
5. **Ship** a focused PR back to `primeodin/vision-caption-loop`:
   - one idea per PR
   - include or update a test when behavior changes
   - say what you ran (`pytest`, `python -m vision_caption_loop --mock`)

## Add a scene

1. Add a `Scene` in `src/vision_caption_loop/scenes.py` with a stable `id` and 3 `must_tags`.
2. Add a loop assertion in `tests/` if the new scene should behave specially.
3. Keep `MockCaptioner` sacred — offline tests must keep working without secrets.
4. Update the README expected stdout if the default scene output changes.

## Good first issues

Scoped tickets (file named in the issue body) live under Issues with the `good first issue` label.
