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

from .game_mode import GameMode
from .game_mod_kind import GameModKind
from .acronym import Acronym
from .generated_mods import (
    # Osu
    EasyOsu, NoFailOsu, HalfTimeOsu, DaycoreOsu, HardRockOsu,
    SuddenDeathOsu, PerfectOsu, DoubleTimeOsu, NightcoreOsu, HiddenOsu,
    TraceableOsu, FlashlightOsu, BlindsOsu, StrictTrackingOsu,
    AccuracyChallengeOsu, TargetPracticeOsu, DifficultyAdjustOsu,
    ClassicOsu, RandomOsu, MirrorOsu, AlternateOsu, SingleTapOsu,
    AutoplayOsu, CinemaOsu, RelaxOsu, AutopilotOsu, SpunOutOsu,
    TransformOsu, WiggleOsu, SpinInOsu, GrowOsu, DeflateOsu,
    WindUpOsu, WindDownOsu, BarrelRollOsu, ApproachDifferentOsu,
    MutedOsu, NoScopeOsu, MagnetisedOsu, RepelOsu, AdaptiveSpeedOsu,
    FreezeFrameOsu, BubblesOsu, SynesthesiaOsu, DepthOsu, BloomOsu,
    TouchDeviceOsu, ScoreV2Osu,
    # Taiko
    EasyTaiko, NoFailTaiko, HalfTimeTaiko, DaycoreTaiko,
    SimplifiedRhythmTaiko, HardRockTaiko, SuddenDeathTaiko, PerfectTaiko,
    DoubleTimeTaiko, NightcoreTaiko, HiddenTaiko, FlashlightTaiko,
    AccuracyChallengeTaiko, RandomTaiko, DifficultyAdjustTaiko,
    ClassicTaiko, SwapTaiko, SingleTapTaiko, ConstantSpeedTaiko,
    AutoplayTaiko, CinemaTaiko, RelaxTaiko, WindUpTaiko, WindDownTaiko,
    MutedTaiko, AdaptiveSpeedTaiko, ScoreV2Taiko,
    # Catch
    EasyCatch, NoFailCatch, HalfTimeCatch, DaycoreCatch, HardRockCatch,
    SuddenDeathCatch, PerfectCatch, DoubleTimeCatch, NightcoreCatch,
    HiddenCatch, FlashlightCatch, AccuracyChallengeCatch,
    DifficultyAdjustCatch, ClassicCatch, MirrorCatch, AutoplayCatch,
    CinemaCatch, RelaxCatch, WindUpCatch, WindDownCatch,
    FloatingFruitsCatch, MutedCatch, NoScopeCatch, MovingFastCatch,
    ScoreV2Catch,
    # Mania
    EasyMania, NoFailMania, HalfTimeMania, DaycoreMania, NoReleaseMania,
    HardRockMania, SuddenDeathMania, PerfectMania, DoubleTimeMania,
    NightcoreMania, FadeInMania, HiddenMania, CoverMania, FlashlightMania,
    AccuracyChallengeMania, RandomMania, DualStagesMania, MirrorMania,
    DifficultyAdjustMania, ClassicMania, InvertMania, ConstantSpeedMania,
    HoldOffMania, OneKeyMania, TwoKeysMania, ThreeKeysMania, FourKeysMania,
    FiveKeysMania, SixKeysMania, SevenKeysMania, EightKeysMania,
    NineKeysMania, TenKeysMania, AutoplayMania, CinemaMania,
    WindUpMania, WindDownMania, MutedMania, AdaptiveSpeedMania,
    ScoreV2Mania,
    # Special
    UnknownMod,
)

from .game_mod import GameMod
from .game_mod_intermode import GameModIntermode
from .game_mods import GameMods
from .game_mods_intermode import GameModsIntermode
from .game_mods_legacy import GameModsLegacy
from .game_mod_simple import GameModSimple, SettingSimple
from . import _patches

__all__ = [
    "GameMode", "GameModKind", "Acronym",
    "GameMod", "GameMods",
    "GameModIntermode", "GameModsIntermode",
    "GameModsLegacy",
    "GameModSimple", "SettingSimple",
    # Individual mod classes
    "EasyOsu", "NoFailOsu", "HalfTimeOsu", "DaycoreOsu", "HardRockOsu",
    "SuddenDeathOsu", "PerfectOsu", "DoubleTimeOsu", "NightcoreOsu", "HiddenOsu",
    "TraceableOsu", "FlashlightOsu", "BlindsOsu", "StrictTrackingOsu",
    "AccuracyChallengeOsu", "TargetPracticeOsu", "DifficultyAdjustOsu",
    "ClassicOsu", "RandomOsu", "MirrorOsu", "AlternateOsu", "SingleTapOsu",
    "AutoplayOsu", "CinemaOsu", "RelaxOsu", "AutopilotOsu", "SpunOutOsu",
    "TransformOsu", "WiggleOsu", "SpinInOsu", "GrowOsu", "DeflateOsu",
    "WindUpOsu", "WindDownOsu", "BarrelRollOsu", "ApproachDifferentOsu",
    "MutedOsu", "NoScopeOsu", "MagnetisedOsu", "RepelOsu", "AdaptiveSpeedOsu",
    "FreezeFrameOsu", "BubblesOsu", "SynesthesiaOsu", "DepthOsu", "BloomOsu",
    "TouchDeviceOsu", "ScoreV2Osu",
    "EasyTaiko", "NoFailTaiko", "HalfTimeTaiko", "DaycoreTaiko",
    "SimplifiedRhythmTaiko", "HardRockTaiko", "SuddenDeathTaiko", "PerfectTaiko",
    "DoubleTimeTaiko", "NightcoreTaiko", "HiddenTaiko", "FlashlightTaiko",
    "AccuracyChallengeTaiko", "RandomTaiko", "DifficultyAdjustTaiko",
    "ClassicTaiko", "SwapTaiko", "SingleTapTaiko", "ConstantSpeedTaiko",
    "AutoplayTaiko", "CinemaTaiko", "RelaxTaiko", "WindUpTaiko", "WindDownTaiko",
    "MutedTaiko", "AdaptiveSpeedTaiko", "ScoreV2Taiko",
    "EasyCatch", "NoFailCatch", "HalfTimeCatch", "DaycoreCatch", "HardRockCatch",
    "SuddenDeathCatch", "PerfectCatch", "DoubleTimeCatch", "NightcoreCatch",
    "HiddenCatch", "FlashlightCatch", "AccuracyChallengeCatch",
    "DifficultyAdjustCatch", "ClassicCatch", "MirrorCatch", "AutoplayCatch",
    "CinemaCatch", "RelaxCatch", "WindUpCatch", "WindDownCatch",
    "FloatingFruitsCatch", "MutedCatch", "NoScopeCatch", "MovingFastCatch",
    "ScoreV2Catch",
    "EasyMania", "NoFailMania", "HalfTimeMania", "DaycoreMania", "NoReleaseMania",
    "HardRockMania", "SuddenDeathMania", "PerfectMania", "DoubleTimeMania",
    "NightcoreMania", "FadeInMania", "HiddenMania", "CoverMania", "FlashlightMania",
    "AccuracyChallengeMania", "RandomMania", "DualStagesMania", "MirrorMania",
    "DifficultyAdjustMania", "ClassicMania", "InvertMania", "ConstantSpeedMania",
    "HoldOffMania", "OneKeyMania", "TwoKeysMania", "ThreeKeysMania", "FourKeysMania",
    "FiveKeysMania", "SixKeysMania", "SevenKeysMania", "EightKeysMania",
    "NineKeysMania", "TenKeysMania", "AutoplayMania", "CinemaMania",
    "WindUpMania", "WindDownMania", "MutedMania", "AdaptiveSpeedMania",
    "ScoreV2Mania",
    "UnknownMod",
]
