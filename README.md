# vision-caption-loop

> Day-7 of PrimeOdin’s daily public builds — a tiny vision caption loop where a draft caption gets verified against must-tags, then refined once.

**Caption. Verify. Refine.** That is the whole trick. Shop teaching: name the part before the story.

## 60-second start

```bash
git clone https://github.com/primeodin/vision-caption-loop.git
cd vision-caption-loop
pip install -e ".[dev]"
pytest
python -m vision_caption_loop --mock
python -m vision_caption_loop --mock --json
```

**Expected stdout** (deterministic on `--mock` — yours should match):

```text
# pytest
.............                                                       [100%]
13 passed

# mock caption loop
[mock] vision caption loop — scene: brake_pads
cues: rusty rotor, worn brake pad, caliper, wheel off
must_tags: brake, pad, rotor

draft:  A shop photo shows a brake, pad, shop part in a typical garage setup.
verify: score=0.67 hit=['brake', 'pad'] miss=['rotor'] ok=False

refine: Close-up of brake, pad, rotor: rusty rotor, with worn brake pad visible. Draft was incomplete; refined to name the parts.
verify: score=1.00 hit=['brake', 'pad', 'rotor'] miss=[] ok=True

[mock] PASS — final caption names all must-tags.
Shop note: Name the part before the rust story — pad vs rotor vs caliper.
```

If the draft already `PASS`es or `rotor` is not in `miss`, the mock or default scene changed — open an issue before "fixing" the table by eye.

## Why a caption loop

A caption is a **claim**. Fluent text can still skip the part a tech needs on the work order.

Three mysteries go away once you run this loop yourself:

- why a pretty draft can fail a boring checklist (`must_tags`)
- why verify-before-trust beats vibes when the model (or you) waves at “shop part”
- why one refine pass is enough for teaching — don’t rewrite for style alone

Deeper shop note: **[why verify](docs/why-verify.md)** — name the part before the rust story.

## The whole loop, in five lines

1. Fix a tiny scene bank (shop “photos” with cues + must-tags).
2. Draft a caption (mock in tests; live optional).
3. Verify: score = fraction of must-tags present as tokens.
4. If anything is missing, refine once with the draft as context.
5. Declare PASS only when the final caption hits every must-tag.

```text
Scene (cues + must_tags)
   |
   v
 Captioner (mock / optional live) ----> draft caption
   |
   v
 Verify (must_tags as tokens) ----> score / hit / miss
   |
   +-- ok? ------------------> PASS (done)
   |
   +-- miss? --> Captioner(refine) --> verify again --> PASS/FAIL
```

Shop rule: keep the must-tags still while you tune the captioner. If you rewrite the checklist every time the model drifts, you are grading the weather.

## Built-in demo

| Piece | What it does |
| --- | --- |
| **MockCaptioner** | Vague draft (drops last must-tag) → refined caption that names all tags. No network. |
| **Scene bank** | Six shop stand-ins: brake pads, breaker panel, radiator hose, kitchen drain, furnace filter, wire nuts. |
| **Default scene** | `brake_pads` — draft misses `rotor`; refine fills it. |
| **`--live`** | Optional OpenAI chat caption behind a flag. Needs `OPENAI_API_KEY`. Tests never use it. |

## Shop tip

When a caption says “engine bay problem,” ask which hose, which clamp, which fluid. Same judgment here: the mock teaches the shape of caption → verify → refine; live vision is the power tool — useful, not for every demo.

## CLI cheatsheet

```bash
python -m vision_caption_loop --mock
python -m vision_caption_loop --mock --json
python -m vision_caption_loop --mock --scene breaker_panel
python -m vision_caption_loop --list-scenes
python -m vision_caption_loop --live   # needs OPENAI_API_KEY
./scripts/smoke.sh
```

## Project layout

```text
src/vision_caption_loop/
  scenes.py    # SCENE_BANK + DEFAULT_SCENE_ID
  caption.py   # MockCaptioner, OpenAICaptioner
  verify.py    # verify_caption → Verdict
  loop.py      # run_loop → draft → verify → refine
  cli.py       # argparse text / JSON
docs/
  why-verify.md
tests/         # pytest — mock path only
scripts/smoke.sh
```

## Good first issues

New to pull requests? Start at [first-commit-ai](https://github.com/primeodin/first-commit-ai), then come back.

- [#1 — ASCII verify scorebar in CLI text mode](https://github.com/primeodin/vision-caption-loop/issues/1)
- [#2 — Add a seventh shop scene to SCENE_BANK](https://github.com/primeodin/vision-caption-loop/issues/2)
- [#3 — Hand-worked verify example in docs/why-verify.md](https://github.com/primeodin/vision-caption-loop/issues/3)

## Daily build series

| Day | Repo |
| --- | --- |
| 01 | [first-commit-ai](https://github.com/primeodin/first-commit-ai) |
| 02 | [notes-rag](https://github.com/primeodin/notes-rag) |
| 03 | [tiny-bpe-tokenizer](https://github.com/primeodin/tiny-bpe-tokenizer) |
| 04 | [tiny-tool-agent](https://github.com/primeodin/tiny-tool-agent) |
| 05 | [prompt-lab](https://github.com/primeodin/prompt-lab) |
| 06 | [embedding-playground](https://github.com/primeodin/embedding-playground) |
| 07 | **vision-caption-loop** (this repo) |

## License

MIT
