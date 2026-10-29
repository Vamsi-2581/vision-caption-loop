"""Mock shop scenes — stand-ins for photos you would caption."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    """A tiny stand-in for an image: id, description cues, must-hit tags."""

    id: str
    cues: tuple[str, ...]
    must_tags: tuple[str, ...]
    shop_note: str


# Fixed bank so mock captions and tests stay deterministic.
SCENE_BANK: tuple[Scene, ...] = (
    Scene(
        id="brake_pads",
        cues=("rusty rotor", "worn brake pad", "caliper", "wheel off"),
        must_tags=("brake", "pad", "rotor"),
        shop_note="Name the part before the rust story — pad vs rotor vs caliper.",
    ),
    Scene(
        id="breaker_panel",
        cues=("open breaker panel", "tripped 20A breaker", "labeled circuits"),
        must_tags=("breaker", "panel", "tripped"),
        shop_note="Caption the panel state (open/tripped) before guessing the short.",
    ),
    Scene(
        id="radiator_hose",
        cues=("swollen upper radiator hose", "clamp", "coolant residue"),
        must_tags=("radiator", "hose", "clamp"),
        shop_note="Swollen hose + crusty clamp = leak risk — say hose, not 'engine'.",
    ),
    Scene(
        id="kitchen_drain",
        cues=("kitchen sink", "standing water", "p-trap under cabinet"),
        must_tags=("drain", "sink", "p-trap"),
        shop_note="Standing water is the symptom; the trap is the part you name.",
    ),
    Scene(
        id="furnace_filter",
        cues=("dirty furnace filter", "hvac slot", "dust mat"),
        must_tags=("furnace", "filter", "dust"),
        shop_note="Caption the filter condition — dirty vs clean — not just 'HVAC'.",
    ),
    Scene(
        id="wire_nuts",
        cues=("junction box", "wire nuts", "ground wire tucked"),
        must_tags=("wire", "nuts", "box"),
        shop_note="Name the fasteners (wire nuts) and the box — not 'electricity'.",
    ),
    Scene(
        id="water_heater_leak",
        cues=("water heater", "drip at pressure relief valve", "wet drain pan", "copper discharge pipe"),
        must_tags=("heater", "valve", "leak"),
        shop_note="Name the leaking relief valve before guessing at the heater tank.",
    ),
)

DEFAULT_SCENE_ID = "brake_pads"


def get_scene(scene_id: str) -> Scene:
    for scene in SCENE_BANK:
        if scene.id == scene_id:
            return scene
    known = ", ".join(s.id for s in SCENE_BANK)
    raise KeyError(f"unknown scene {scene_id!r}; known: {known}")
