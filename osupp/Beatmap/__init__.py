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

import os
import sys

_pkg_dir = os.path.dirname(__file__)
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from beatmap import Beatmap
from section.difficulty import Difficulty
from section.enums import GameMode, HitSoundType, SampleBank, SplineType
from section.general import General
from section.metadata import Metadata
from section.timing_points import (
    ControlPoints,
    DifficultyPoint,
    EffectPoint,
    SamplePoint,
    TimingPoint,
    TimingPointsState,
)

__all__ = [
    "Beatmap",
    "ControlPoints",
    "DifficultyPoint",
    "EffectPoint",
    "SamplePoint",
    "TimingPoint",
    "TimingPointsState",
    "GameMode",
    "SampleBank",
    "HitSoundType",
    "SplineType",
    "General",
    "Difficulty",
    "Metadata",
]
