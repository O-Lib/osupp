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
from typing import ClassVar
from .mode import GameMode
from .mods import PerformanceMods

def _difficulty_range(difficulty: float, min_val: float, mid_val: float, max_val: float) -> float:
    if difficulty > 5.0:
        return mid_val + (max_val - mid_val) * (difficulty - 5.0) / 5.0
    if difficulty < 5.0:
        return mid_val - (mid_val - min_val) * (5.0 - difficulty) / 5.0
    return mid_val

def _inverse_difficulty_range(time: float, min_val: float, mid_val: float, max_val: float) -> float:
    if time > mid_val:
        return 5.0 - (time - mid_val) * 5.0 / (min_val - mid_val)
    if time < mid_val:
        return 5.0 + (mid_val - time) * 5.0 / (mid_val - max_val)
    return 5.0

@dataclass(slots=True)
class GameModeHitWindows:
    min: float
    mid: float
    max: float

    def difficulty_range(self, difficulty: float) -> float:
        return _difficulty_range(difficulty, self.min, self.mid, self.max)

    def inverse_difficulty_range(self, time: float) -> float:
        return _inverse_difficulty_range(time, self.min, self.mid, self.max)


AR_WINDOWS = GameModeHitWindows(min=1800.0, mid=1200.0, max=450.0)

OSU_GREAT = GameModeHitWindows(min=80.0, mid=50.0, max=20.0)
OSU_OK = GameModeHitWindows(min=140.0, mid=100.0, max=60.0)
OSU_MEH = GameModeHitWindows(min=200.0, mid=150.0, max=100.0)

TAIKO_GREAT = GameModeHitWindows(min=50.0, mid=35.0, max=20.0)
TAIKO_OK = GameModeHitWindows(min=120.0, mid=80.0, max=50.0)

MANIA_PERFECT = GameModeHitWindows(min=22.4, mid=19.4, max=13.9)
MANIA_GREAT = GameModeHitWindows(min=64.0, mid=49.0, max=34.0)
MANIA_GOOD = GameModeHitWindows(min=97.0, mid=82.0, max=67.0)
MANIA_OK = GameModeHitWindows(min=127.0, mid=112.0, max=97.0)
MANIA_MEH = GameModeHitWindows(min=151.0, mid=136.0, max=121.0)


@dataclass(slots=True)
class HitWindows:
    ar: float | None = None
    od_perfect: float | None = None
    od_great: float | None = None
    od_good: float | None = None
    od_ok: float | None = None
    od_meh: float | None = None


@dataclass(slots=True)
class AdjustedBeatmapAttributes:
    cs: float
    ar: float
    od: float
    hp: float
    clock_rate: float
    hit_windows: HitWindows

    @classmethod
    def create(
            cls,
            base_cs: float,
            base_ar: float,
            base_od: float,
            base_hp: float,
            mode: GameMode,
            mods: PerformanceMods
    ) -> "AdjustedBeatmapAttributes":
        cs = base_cs
        ar = base_ar
        od = base_od
        hp = base_hp

        if mods.ez:
            cs *= 0.5
            ar *= 0.5
            hp *= 0.5
            if mode != GameMode.MANIA:
                od *= 0.5
        elif mods.hr:
            hp = min(hp * 1.4, 10.0)
            if mode != GameMode.MANIA:
                cs = min(cs * 1.3, 10.0)
                ar = min(ar * 1.4, 10.0)
                od = min(od * 1.4, 10.0)

        clock_rate = mods.clock_rate

        final_ar = ar
        final_od = od

        if mode in (GameMode.OSU, GameMode.CATCH):
            preempt = AR_WINDOWS.difficulty_range(ar) / clock_rate
            final_ar = AR_WINDOWS.inverse_difficulty_range(preempt)

        if mode == GameMode.OSU:
            great_window = OSU_GREAT.difficulty_range(od) / clock_rate
            final_od = OSU_GREAT.inverse_difficulty_range(great_window)
        elif mode == GameMode.TAIKO:
            great_window = TAIKO_GREAT.difficulty_range(od) / clock_rate
            final_od = TAIKO_GREAT.inverse_difficulty_range(great_window)
        elif mode == GameMode.MANIA:
            perfect_window = MANIA_PERFECT.difficulty_range(od)
            if mods.ez:
                perfect_window /= (1.0 / 1.4)
            elif mods.hr:
                perfect_window /= 1.4
            final_od = MANIA_PERFECT.inverse_difficulty_range(perfect_window)

        hw = HitWindows()

        if mode in (GameMode.OSU, GameMode.CATCH):
            hw.ar = AR_WINDOWS.difficulty_range(final_ar) / clock_rate

        if mode == GameMode.OSU:
            hw.od_great = (int(OSU_GREAT.difficulty_range(final_od)) - 0.5) / clock_rate
            hw.od_ok = (int(OSU_OK.difficulty_range(final_od)) - 0.5) / clock_rate
            hw.od_meh = (int(OSU_MEH.difficulty_range(final_od)) - 0.5) / clock_rate
        elif mode == GameMode.TAIKO:
            hw.od_great = (int(TAIKO_GREAT.difficulty_range(final_od)) - 0.5) / clock_rate
            hw.od_ok = (int(TAIKO_OK.difficulty_range(final_od)) - 0.5) / clock_rate
        elif mode == GameMode.MANIA:
            hw.od_perfect = int(MANIA_PERFECT.difficulty_range(final_od)) + 0.5
            hw.od_great = int(MANIA_GREAT.difficulty_range(final_od)) + 0.5
            hw.od_good = int(MANIA_GOOD.difficulty_range(final_od)) + 0.5
            hw.od_ok = int(MANIA_OK.difficulty_range(final_od)) + 0.5
            hw.od_meh = int(MANIA_MEH.difficulty_range(final_od)) + 0.5

        return cls(
            cs=cs,
            ar=final_ar,
            od=final_od,
            hp=hp,
            clock_rate=clock_rate,
            hit_windows=hw
        )