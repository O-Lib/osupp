"""
MIT License

Copyright (c) 2026-Present O!Lib Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

class Reflection(IntEnum):
    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2
    BOTH = 3

class ModBits(IntFlag):
    NO_FAIL = 1 << 0
    EASY = 1 << 1
    TOUCH_DEVICE = 1 << 2
    HIDDEN = 1 << 3
    HARD_ROCK = 1 << 4
    DOUBLE_TIME = 1 << 6
    RELAX = 1 << 7
    HALF_TIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    SPUN_OUT = 1 << 12
    AUTOPILOT = 1 << 13
    SCORE_V2 = 1 << 29

    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    KEY9 = 1 << 24
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28

@dataclass(slots=True)
class PerformanceMods:
    bits: int = 0
    clock_rate: float = 1.0
    hardrock_offsets: bool = False
    no_slider_head_acc: bool = True
    reflection: Reflection = Reflection.NONE
    mania_keys: float | None = None
    scroll_speed: float | None = None
    random_seed: int | None = None
    attraction_strength: float | None = None
    deflate_start_scale: float | None = None
    hd_only_fade_approach_circles: bool | None = None

    nf: bool = False
    ez: bool = False
    td: bool = False
    hd: bool = False
    hr: bool = False
    rx: bool = False
    fl: bool = False
    so: bool = False
    ap: bool = False
    sv2: bool = False

    @classmethod
    def from_mods(cls, mods: Any) -> "PerformanceMods":
        bits = 0
        if isinstance(mods, int):
            bits = mods
        elif hasattr(mods, "bits") and callable(mods.bits):
            bits = mods.bits()

        nf = bool(bits & ModBits.NO_FAIL)
        ez = bool(bits & ModBits.EASY)
        td = bool(bits & ModBits.TOUCH_DEVICE)
        hd = bool(bits & ModBits.HIDDEN)
        hr = bool(bits & ModBits.HARD_ROCK)
        rx = bool(bits & ModBits.RELAX)
        fl = bool(bits & ModBits.FLASHLIGHT)
        so = bool(bits & ModBits.SPUN_OUT)
        ap = bool(bits & ModBits.AUTOPILOT)
        sv2 = bool(bits & ModBits.SCORE_V2)

        clock_rate = 1.0
        if (bits & ModBits.DOUBLE_TIME) or (bits & ModBits.NIGHTCORE):
            clock_rate = 1.5
        elif (bits & ModBits.HALF_TIME):
            clock_rate = 0.75

        hardrock_offsets = hr
        reflection = Reflection.VERTICAL if hr else Reflection.NONE
        mania_keys = cls._extract_legacy_mania_keys(bits)

        scroll_speed = None
        random_seed = None
        attraction_strength = None
        deflate_start_scale = None
        hd_only_fade_approach_circles = None

        if hasattr(mods, "__iter__"):
            for m in mods:
                if hasattr(m, "clock_rate") and callable(m.clock_rate):
                    cr = m.clock_rate()
                    if cr is not None:
                        clock_rate = cr

                if hasattr(m, "hard_rock_offsets"):
                    hardrock_offsets = m.hard_rock_offsets

                if hasattr(m, "scroll_speed"):
                    scroll_speed = m.scroll_speed
                if hasattr(m, "seed") and m.seed is not None:
                    random_seed = m.seed

                if hasattr(m, "attraction_strength"):
                    attraction_strength = m.attraction_strength
                if hasattr(m, "start_scale"):
                    deflate_start_scale = m.start_scale
                if hasattr(m, "only_fade_approach_circles"):
                    hd_only_fade_approach_circles = m.only_fade_approach_circles

                m_type = type(m).__name__
                if m_type == "MirrorOsu":
                    ref = getattr(m, "reflection", None)
                    if ref is None: reflection = Reflection.HORIZONTAL
                    elif ref == "1": reflection = Reflection.VERTICAL
                    elif ref == "2": reflection = Reflection.BOTH
                    else: reflection = Reflection.NONE
                elif m_type == "MirrorCatch":
                    reflection = Reflection.HORIZONTAL

                if m_type.endswith("KeysMania"):
                    keys_str = m_type.replace("KeysMania", "").replace("KeyMania", "")
                    keys_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5, "Six":6, "Seven":7, "Eight":8, "Nine":9, "Ten":10}
                    if keys_str in keys_map:
                        mania_keys = float(keys_map[keys_str])

        return cls(
            bits=bits,
            clock_rate=clock_rate,
            hardrock_offsets=hardrock_offsets,
            no_slider_head_acc=True,
            reflection=reflection,
            mania_keys=mania_keys,
            scroll_speed=scroll_speed,
            random_seed=random_seed,
            attraction_strength=attraction_strength,
            deflate_start_scale=deflate_start_scale,
            hd_only_fade_approach_circles=hd_only_fade_approach_circles,
            nf=nf, ez=ez, td=td, hd=hd, hr=hr, rx=rx, fl=fl, so=so, ap=ap, sv2=sv2
        )

    @staticmethod
    def _extract_legacy_mania_keys(bits: int) -> float | None:
        if bits & ModBits.KEY1: return 1.0
        if bits & ModBits.KEY2: return 2.0
        if bits & ModBits.KEY3: return 3.0
        if bits & ModBits.KEY4: return 4.0
        if bits & ModBits.KEY5: return 5.0
        if bits & ModBits.KEY6: return 6.0
        if bits & ModBits.KEY7: return 7.0
        if bits & ModBits.KEY8: return 8.0
        if bits & ModBits.KEY9: return 9.0
        return None