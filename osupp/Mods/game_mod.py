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

from __future__ import annotations
from typing import Optional, Union
from .game_mode import GameMode
from .game_mod_kind import GameModKind
from .acronym import Acronym
from .generated_mods import (
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
    EasyTaiko, NoFailTaiko, HalfTimeTaiko, DaycoreTaiko,
    SimplifiedRhythmTaiko, HardRockTaiko, SuddenDeathTaiko, PerfectTaiko,
    DoubleTimeTaiko, NightcoreTaiko, HiddenTaiko, FlashlightTaiko,
    AccuracyChallengeTaiko, RandomTaiko, DifficultyAdjustTaiko,
    ClassicTaiko, SwapTaiko, SingleTapTaiko, ConstantSpeedTaiko,
    AutoplayTaiko, CinemaTaiko, RelaxTaiko, WindUpTaiko, WindDownTaiko,
    MutedTaiko, AdaptiveSpeedTaiko, ScoreV2Taiko,
    EasyCatch, NoFailCatch, HalfTimeCatch, DaycoreCatch, HardRockCatch,
    SuddenDeathCatch, PerfectCatch, DoubleTimeCatch, NightcoreCatch,
    HiddenCatch, FlashlightCatch, AccuracyChallengeCatch,
    DifficultyAdjustCatch, ClassicCatch, MirrorCatch, AutoplayCatch,
    CinemaCatch, RelaxCatch, WindUpCatch, WindDownCatch,
    FloatingFruitsCatch, MutedCatch, NoScopeCatch, MovingFastCatch,
    ScoreV2Catch,
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
    UnknownMod, UnknownOsu, UnknownTaiko, UnknownCatch, UnknownMania,
)

_VARIANT_MAP: dict[str, tuple[type, Optional[GameMode]]] = {
    "EasyOsu": (EasyOsu, GameMode.Osu), "NoFailOsu": (NoFailOsu, GameMode.Osu),
    "HalfTimeOsu": (HalfTimeOsu, GameMode.Osu), "DaycoreOsu": (DaycoreOsu, GameMode.Osu),
    "HardRockOsu": (HardRockOsu, GameMode.Osu), "SuddenDeathOsu": (SuddenDeathOsu, GameMode.Osu),
    "PerfectOsu": (PerfectOsu, GameMode.Osu), "DoubleTimeOsu": (DoubleTimeOsu, GameMode.Osu),
    "NightcoreOsu": (NightcoreOsu, GameMode.Osu), "HiddenOsu": (HiddenOsu, GameMode.Osu),
    "TraceableOsu": (TraceableOsu, GameMode.Osu), "FlashlightOsu": (FlashlightOsu, GameMode.Osu),
    "BlindsOsu": (BlindsOsu, GameMode.Osu), "StrictTrackingOsu": (StrictTrackingOsu, GameMode.Osu),
    "AccuracyChallengeOsu": (AccuracyChallengeOsu, GameMode.Osu),
    "TargetPracticeOsu": (TargetPracticeOsu, GameMode.Osu),
    "DifficultyAdjustOsu": (DifficultyAdjustOsu, GameMode.Osu),
    "ClassicOsu": (ClassicOsu, GameMode.Osu), "RandomOsu": (RandomOsu, GameMode.Osu),
    "MirrorOsu": (MirrorOsu, GameMode.Osu), "AlternateOsu": (AlternateOsu, GameMode.Osu),
    "SingleTapOsu": (SingleTapOsu, GameMode.Osu), "AutoplayOsu": (AutoplayOsu, GameMode.Osu),
    "CinemaOsu": (CinemaOsu, GameMode.Osu), "RelaxOsu": (RelaxOsu, GameMode.Osu),
    "AutopilotOsu": (AutopilotOsu, GameMode.Osu), "SpunOutOsu": (SpunOutOsu, GameMode.Osu),
    "TransformOsu": (TransformOsu, GameMode.Osu), "WiggleOsu": (WiggleOsu, GameMode.Osu),
    "SpinInOsu": (SpinInOsu, GameMode.Osu), "GrowOsu": (GrowOsu, GameMode.Osu),
    "DeflateOsu": (DeflateOsu, GameMode.Osu), "WindUpOsu": (WindUpOsu, GameMode.Osu),
    "WindDownOsu": (WindDownOsu, GameMode.Osu), "BarrelRollOsu": (BarrelRollOsu, GameMode.Osu),
    "ApproachDifferentOsu": (ApproachDifferentOsu, GameMode.Osu),
    "MutedOsu": (MutedOsu, GameMode.Osu), "NoScopeOsu": (NoScopeOsu, GameMode.Osu),
    "MagnetisedOsu": (MagnetisedOsu, GameMode.Osu), "RepelOsu": (RepelOsu, GameMode.Osu),
    "AdaptiveSpeedOsu": (AdaptiveSpeedOsu, GameMode.Osu),
    "FreezeFrameOsu": (FreezeFrameOsu, GameMode.Osu), "BubblesOsu": (BubblesOsu, GameMode.Osu),
    "SynesthesiaOsu": (SynesthesiaOsu, GameMode.Osu), "DepthOsu": (DepthOsu, GameMode.Osu),
    "BloomOsu": (BloomOsu, GameMode.Osu), "TouchDeviceOsu": (TouchDeviceOsu, GameMode.Osu),
    "ScoreV2Osu": (ScoreV2Osu, GameMode.Osu),
    "EasyTaiko": (EasyTaiko, GameMode.Taiko), "NoFailTaiko": (NoFailTaiko, GameMode.Taiko),
    "HalfTimeTaiko": (HalfTimeTaiko, GameMode.Taiko), "DaycoreTaiko": (DaycoreTaiko, GameMode.Taiko),
    "SimplifiedRhythmTaiko": (SimplifiedRhythmTaiko, GameMode.Taiko),
    "HardRockTaiko": (HardRockTaiko, GameMode.Taiko),
    "SuddenDeathTaiko": (SuddenDeathTaiko, GameMode.Taiko),
    "PerfectTaiko": (PerfectTaiko, GameMode.Taiko), "DoubleTimeTaiko": (DoubleTimeTaiko, GameMode.Taiko),
    "NightcoreTaiko": (NightcoreTaiko, GameMode.Taiko), "HiddenTaiko": (HiddenTaiko, GameMode.Taiko),
    "FlashlightTaiko": (FlashlightTaiko, GameMode.Taiko),
    "AccuracyChallengeTaiko": (AccuracyChallengeTaiko, GameMode.Taiko),
    "RandomTaiko": (RandomTaiko, GameMode.Taiko),
    "DifficultyAdjustTaiko": (DifficultyAdjustTaiko, GameMode.Taiko),
    "ClassicTaiko": (ClassicTaiko, GameMode.Taiko), "SwapTaiko": (SwapTaiko, GameMode.Taiko),
    "SingleTapTaiko": (SingleTapTaiko, GameMode.Taiko),
    "ConstantSpeedTaiko": (ConstantSpeedTaiko, GameMode.Taiko),
    "AutoplayTaiko": (AutoplayTaiko, GameMode.Taiko), "CinemaTaiko": (CinemaTaiko, GameMode.Taiko),
    "RelaxTaiko": (RelaxTaiko, GameMode.Taiko), "WindUpTaiko": (WindUpTaiko, GameMode.Taiko),
    "WindDownTaiko": (WindDownTaiko, GameMode.Taiko), "MutedTaiko": (MutedTaiko, GameMode.Taiko),
    "AdaptiveSpeedTaiko": (AdaptiveSpeedTaiko, GameMode.Taiko),
    "ScoreV2Taiko": (ScoreV2Taiko, GameMode.Taiko),
    "EasyCatch": (EasyCatch, GameMode.Catch), "NoFailCatch": (NoFailCatch, GameMode.Catch),
    "HalfTimeCatch": (HalfTimeCatch, GameMode.Catch), "DaycoreCatch": (DaycoreCatch, GameMode.Catch),
    "HardRockCatch": (HardRockCatch, GameMode.Catch),
    "SuddenDeathCatch": (SuddenDeathCatch, GameMode.Catch),
    "PerfectCatch": (PerfectCatch, GameMode.Catch), "DoubleTimeCatch": (DoubleTimeCatch, GameMode.Catch),
    "NightcoreCatch": (NightcoreCatch, GameMode.Catch), "HiddenCatch": (HiddenCatch, GameMode.Catch),
    "FlashlightCatch": (FlashlightCatch, GameMode.Catch),
    "AccuracyChallengeCatch": (AccuracyChallengeCatch, GameMode.Catch),
    "DifficultyAdjustCatch": (DifficultyAdjustCatch, GameMode.Catch),
    "ClassicCatch": (ClassicCatch, GameMode.Catch), "MirrorCatch": (MirrorCatch, GameMode.Catch),
    "AutoplayCatch": (AutoplayCatch, GameMode.Catch), "CinemaCatch": (CinemaCatch, GameMode.Catch),
    "RelaxCatch": (RelaxCatch, GameMode.Catch), "WindUpCatch": (WindUpCatch, GameMode.Catch),
    "WindDownCatch": (WindDownCatch, GameMode.Catch),
    "FloatingFruitsCatch": (FloatingFruitsCatch, GameMode.Catch),
    "MutedCatch": (MutedCatch, GameMode.Catch), "NoScopeCatch": (NoScopeCatch, GameMode.Catch),
    "MovingFastCatch": (MovingFastCatch, GameMode.Catch),
    "ScoreV2Catch": (ScoreV2Catch, GameMode.Catch),
    "EasyMania": (EasyMania, GameMode.Mania), "NoFailMania": (NoFailMania, GameMode.Mania),
    "HalfTimeMania": (HalfTimeMania, GameMode.Mania), "DaycoreMania": (DaycoreMania, GameMode.Mania),
    "NoReleaseMania": (NoReleaseMania, GameMode.Mania),
    "HardRockMania": (HardRockMania, GameMode.Mania),
    "SuddenDeathMania": (SuddenDeathMania, GameMode.Mania),
    "PerfectMania": (PerfectMania, GameMode.Mania), "DoubleTimeMania": (DoubleTimeMania, GameMode.Mania),
    "NightcoreMania": (NightcoreMania, GameMode.Mania), "FadeInMania": (FadeInMania, GameMode.Mania),
    "HiddenMania": (HiddenMania, GameMode.Mania), "CoverMania": (CoverMania, GameMode.Mania),
    "FlashlightMania": (FlashlightMania, GameMode.Mania),
    "AccuracyChallengeMania": (AccuracyChallengeMania, GameMode.Mania),
    "RandomMania": (RandomMania, GameMode.Mania), "DualStagesMania": (DualStagesMania, GameMode.Mania),
    "MirrorMania": (MirrorMania, GameMode.Mania),
    "DifficultyAdjustMania": (DifficultyAdjustMania, GameMode.Mania),
    "ClassicMania": (ClassicMania, GameMode.Mania), "InvertMania": (InvertMania, GameMode.Mania),
    "ConstantSpeedMania": (ConstantSpeedMania, GameMode.Mania),
    "HoldOffMania": (HoldOffMania, GameMode.Mania), "OneKeyMania": (OneKeyMania, GameMode.Mania),
    "TwoKeysMania": (TwoKeysMania, GameMode.Mania), "ThreeKeysMania": (ThreeKeysMania, GameMode.Mania),
    "FourKeysMania": (FourKeysMania, GameMode.Mania), "FiveKeysMania": (FiveKeysMania, GameMode.Mania),
    "SixKeysMania": (SixKeysMania, GameMode.Mania), "SevenKeysMania": (SevenKeysMania, GameMode.Mania),
    "EightKeysMania": (EightKeysMania, GameMode.Mania), "NineKeysMania": (NineKeysMania, GameMode.Mania),
    "TenKeysMania": (TenKeysMania, GameMode.Mania), "AutoplayMania": (AutoplayMania, GameMode.Mania),
    "CinemaMania": (CinemaMania, GameMode.Mania), "WindUpMania": (WindUpMania, GameMode.Mania),
    "WindDownMania": (WindDownMania, GameMode.Mania), "MutedMania": (MutedMania, GameMode.Mania),
    "AdaptiveSpeedMania": (AdaptiveSpeedMania, GameMode.Mania),
    "ScoreV2Mania": (ScoreV2Mania, GameMode.Mania),
    "UnknownOsu": (UnknownOsu, GameMode.Osu), "UnknownTaiko": (UnknownTaiko, GameMode.Taiko),
    "UnknownCatch": (UnknownCatch, GameMode.Catch), "UnknownMania": (UnknownMania, GameMode.Mania),
    "UnknownMod": (UnknownMod, None),
}

_ACR_MODE_MAP: dict[tuple[str, GameMode], type] = {
    ("EZ", GameMode.Osu): EasyOsu, ("NF", GameMode.Osu): NoFailOsu,
    ("HT", GameMode.Osu): HalfTimeOsu, ("DC", GameMode.Osu): DaycoreOsu,
    ("HR", GameMode.Osu): HardRockOsu, ("SD", GameMode.Osu): SuddenDeathOsu,
    ("PF", GameMode.Osu): PerfectOsu, ("DT", GameMode.Osu): DoubleTimeOsu,
    ("NC", GameMode.Osu): NightcoreOsu, ("HD", GameMode.Osu): HiddenOsu,
    ("TC", GameMode.Osu): TraceableOsu, ("FL", GameMode.Osu): FlashlightOsu,
    ("BL", GameMode.Osu): BlindsOsu, ("ST", GameMode.Osu): StrictTrackingOsu,
    ("AC", GameMode.Osu): AccuracyChallengeOsu, ("TP", GameMode.Osu): TargetPracticeOsu,
    ("DA", GameMode.Osu): DifficultyAdjustOsu, ("CL", GameMode.Osu): ClassicOsu,
    ("RD", GameMode.Osu): RandomOsu, ("MR", GameMode.Osu): MirrorOsu,
    ("AL", GameMode.Osu): AlternateOsu, ("SG", GameMode.Osu): SingleTapOsu,
    ("AT", GameMode.Osu): AutoplayOsu, ("CN", GameMode.Osu): CinemaOsu,
    ("RX", GameMode.Osu): RelaxOsu, ("AP", GameMode.Osu): AutopilotOsu,
    ("SO", GameMode.Osu): SpunOutOsu, ("TR", GameMode.Osu): TransformOsu,
    ("WG", GameMode.Osu): WiggleOsu, ("SI", GameMode.Osu): SpinInOsu,
    ("GR", GameMode.Osu): GrowOsu, ("DF", GameMode.Osu): DeflateOsu,
    ("WU", GameMode.Osu): WindUpOsu, ("WD", GameMode.Osu): WindDownOsu,
    ("BR", GameMode.Osu): BarrelRollOsu, ("AD", GameMode.Osu): ApproachDifferentOsu,
    ("MU", GameMode.Osu): MutedOsu, ("NS", GameMode.Osu): NoScopeOsu,
    ("MG", GameMode.Osu): MagnetisedOsu, ("RP", GameMode.Osu): RepelOsu,
    ("AS", GameMode.Osu): AdaptiveSpeedOsu, ("FR", GameMode.Osu): FreezeFrameOsu,
    ("BU", GameMode.Osu): BubblesOsu, ("SY", GameMode.Osu): SynesthesiaOsu,
    ("DP", GameMode.Osu): DepthOsu, ("BM", GameMode.Osu): BloomOsu,
    ("TD", GameMode.Osu): TouchDeviceOsu, ("SV2", GameMode.Osu): ScoreV2Osu,
    ("EZ", GameMode.Taiko): EasyTaiko, ("NF", GameMode.Taiko): NoFailTaiko,
    ("HT", GameMode.Taiko): HalfTimeTaiko, ("DC", GameMode.Taiko): DaycoreTaiko,
    ("SR", GameMode.Taiko): SimplifiedRhythmTaiko, ("HR", GameMode.Taiko): HardRockTaiko,
    ("SD", GameMode.Taiko): SuddenDeathTaiko, ("PF", GameMode.Taiko): PerfectTaiko,
    ("DT", GameMode.Taiko): DoubleTimeTaiko, ("NC", GameMode.Taiko): NightcoreTaiko,
    ("HD", GameMode.Taiko): HiddenTaiko, ("FL", GameMode.Taiko): FlashlightTaiko,
    ("AC", GameMode.Taiko): AccuracyChallengeTaiko, ("RD", GameMode.Taiko): RandomTaiko,
    ("DA", GameMode.Taiko): DifficultyAdjustTaiko, ("CL", GameMode.Taiko): ClassicTaiko,
    ("SW", GameMode.Taiko): SwapTaiko, ("SG", GameMode.Taiko): SingleTapTaiko,
    ("CS", GameMode.Taiko): ConstantSpeedTaiko, ("AT", GameMode.Taiko): AutoplayTaiko,
    ("CN", GameMode.Taiko): CinemaTaiko, ("RX", GameMode.Taiko): RelaxTaiko,
    ("WU", GameMode.Taiko): WindUpTaiko, ("WD", GameMode.Taiko): WindDownTaiko,
    ("MU", GameMode.Taiko): MutedTaiko, ("AS", GameMode.Taiko): AdaptiveSpeedTaiko,
    ("SV2", GameMode.Taiko): ScoreV2Taiko,
    ("EZ", GameMode.Catch): EasyCatch, ("NF", GameMode.Catch): NoFailCatch,
    ("HT", GameMode.Catch): HalfTimeCatch, ("DC", GameMode.Catch): DaycoreCatch,
    ("HR", GameMode.Catch): HardRockCatch, ("SD", GameMode.Catch): SuddenDeathCatch,
    ("PF", GameMode.Catch): PerfectCatch, ("DT", GameMode.Catch): DoubleTimeCatch,
    ("NC", GameMode.Catch): NightcoreCatch, ("HD", GameMode.Catch): HiddenCatch,
    ("FL", GameMode.Catch): FlashlightCatch, ("AC", GameMode.Catch): AccuracyChallengeCatch,
    ("DA", GameMode.Catch): DifficultyAdjustCatch, ("CL", GameMode.Catch): ClassicCatch,
    ("MR", GameMode.Catch): MirrorCatch, ("AT", GameMode.Catch): AutoplayCatch,
    ("CN", GameMode.Catch): CinemaCatch, ("RX", GameMode.Catch): RelaxCatch,
    ("WU", GameMode.Catch): WindUpCatch, ("WD", GameMode.Catch): WindDownCatch,
    ("FF", GameMode.Catch): FloatingFruitsCatch, ("MU", GameMode.Catch): MutedCatch,
    ("NS", GameMode.Catch): NoScopeCatch, ("MF", GameMode.Catch): MovingFastCatch,
    ("SV2", GameMode.Catch): ScoreV2Catch,
    ("EZ", GameMode.Mania): EasyMania, ("NF", GameMode.Mania): NoFailMania,
    ("HT", GameMode.Mania): HalfTimeMania, ("DC", GameMode.Mania): DaycoreMania,
    ("NR", GameMode.Mania): NoReleaseMania, ("HR", GameMode.Mania): HardRockMania,
    ("SD", GameMode.Mania): SuddenDeathMania, ("PF", GameMode.Mania): PerfectMania,
    ("DT", GameMode.Mania): DoubleTimeMania, ("NC", GameMode.Mania): NightcoreMania,
    ("FI", GameMode.Mania): FadeInMania, ("HD", GameMode.Mania): HiddenMania,
    ("CO", GameMode.Mania): CoverMania, ("FL", GameMode.Mania): FlashlightMania,
    ("AC", GameMode.Mania): AccuracyChallengeMania, ("RD", GameMode.Mania): RandomMania,
    ("DS", GameMode.Mania): DualStagesMania, ("MR", GameMode.Mania): MirrorMania,
    ("DA", GameMode.Mania): DifficultyAdjustMania, ("CL", GameMode.Mania): ClassicMania,
    ("IN", GameMode.Mania): InvertMania, ("CS", GameMode.Mania): ConstantSpeedMania,
    ("HO", GameMode.Mania): HoldOffMania, ("1K", GameMode.Mania): OneKeyMania,
    ("2K", GameMode.Mania): TwoKeysMania, ("3K", GameMode.Mania): ThreeKeysMania,
    ("4K", GameMode.Mania): FourKeysMania, ("5K", GameMode.Mania): FiveKeysMania,
    ("6K", GameMode.Mania): SixKeysMania, ("7K", GameMode.Mania): SevenKeysMania,
    ("8K", GameMode.Mania): EightKeysMania, ("9K", GameMode.Mania): NineKeysMania,
    ("10K", GameMode.Mania): TenKeysMania, ("AT", GameMode.Mania): AutoplayMania,
    ("CN", GameMode.Mania): CinemaMania, ("WU", GameMode.Mania): WindUpMania,
    ("WD", GameMode.Mania): WindDownMania, ("MU", GameMode.Mania): MutedMania,
    ("AS", GameMode.Mania): AdaptiveSpeedMania, ("SV2", GameMode.Mania): ScoreV2Mania,
}

_UNKNOWN_FOR_MODE: dict[GameMode, type] = {
    GameMode.Osu: UnknownOsu, GameMode.Taiko: UnknownTaiko,
    GameMode.Catch: UnknownCatch, GameMode.Mania: UnknownMania,
}


class GameMod:
    __slots__ = ("_variant", "_inner")

    def __init__(self, inner) -> None:
        self._inner = inner
        self._variant = type(inner).__name__

    @classmethod
    def new(cls, acronym: Union[str, "Acronym"], mode: "GameMode") -> "GameMod":
        s = str(acronym).upper()
        inner_cls = _ACR_MODE_MAP.get((s, mode))
        if inner_cls is not None:
            return cls(inner_cls())
        unknown_cls = _UNKNOWN_FOR_MODE.get(mode, UnknownMod)
        return cls(unknown_cls(acronym_str=s))

    @property
    def inner(self):
        return self._inner

    @property
    def variant(self) -> str:
        return self._variant

    def acronym(self) -> "Acronym":
        return self._inner.acronym()

    def description(self) -> str:
        return type(self._inner).description()

    def kind(self) -> "GameModKind":
        return type(self._inner).kind()

    def bits(self) -> Optional[int]:
        return type(self._inner).bits()

    def incompatible_mods(self) -> list:
        return type(self._inner).incompatible_mods()

    def mode(self) -> Optional["GameMode"]:
        return _VARIANT_MAP.get(self._variant, (None, None))[1]

    def intermode(self):
        from .game_mod_intermode import GameModIntermode
        return GameModIntermode.from_acronym(str(self.acronym()))

    def into_simple(self):
        return self._inner.to_simple()

    def is_unknown(self) -> bool:
        return isinstance(self._inner, UnknownMod)

    def to_dict(self) -> dict:
        from dataclasses import fields as dc_fields
        settings = {}
        try:
            for f in dc_fields(self._inner):
                val = getattr(self._inner, f.name)
                if val is not None and f.name != "acronym_str":
                    settings[f.name] = val
        except TypeError:
            pass
        result: dict = {"acronym": str(self.acronym())}
        if settings:
            result["settings"] = settings
        return result

    @classmethod
    def from_dict(cls, data: dict, mode: Optional["GameMode"] = None,
                  deny_unknown_fields: bool = False) -> "GameMod":
        from dataclasses import fields as dc_fields
        acronym = data.get("acronym", "")
        settings = data.get("settings", {})

        def _apply(gm: "GameMod") -> "GameMod":
            inner = gm._inner
            if not settings:
                return gm
            try:
                valid = {f.name for f in dc_fields(inner)}
            except TypeError:
                return gm
            for k, v in settings.items():
                if k in valid:
                    setattr(inner, k, v)
                elif deny_unknown_fields:
                    raise ValueError(f"Unknown field {k!r} for mod {acronym!r}")
            return gm

        if mode is not None:
            return _apply(cls.new(acronym, mode))
        for m in (GameMode.Osu, GameMode.Taiko, GameMode.Catch, GameMode.Mania):
            candidate = cls.new(acronym, m)
            if isinstance(candidate._inner, UnknownMod):
                continue
            if deny_unknown_fields:
                try:
                    return _apply(cls.new(acronym, m))
                except ValueError:
                    continue
            return _apply(candidate)
        return _apply(cls.new(acronym, GameMode.Osu))

    def to_json(self) -> str:
        import json; return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str, mode: Optional["GameMode"] = None,
                  deny_unknown_fields: bool = False) -> "GameMod":
        import json; return cls.from_dict(json.loads(s), mode=mode, deny_unknown_fields=deny_unknown_fields)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GameMod):
            return self._variant == other._variant and self._inner == other._inner
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._variant, str(self.acronym())))

    def __repr__(self) -> str:
        return f"GameMod({self._inner!r})"

    def __str__(self) -> str:
        return str(self.acronym())

    def __lt__(self, other: "GameMod") -> bool:
        m_self = self.mode(); m_other = other.mode()
        mv = lambda m: m.value if m is not None else -1
        return (mv(m_self), str(self.acronym())) < (mv(m_other), str(other.acronym()))


def _attach_constructors():
    for name, (inner_cls, _) in _VARIANT_MAP.items():
        def make_factory(ic):
            @staticmethod
            def factory(**kwargs):
                return GameMod(ic(**kwargs))
            return factory
        setattr(GameMod, name, make_factory(inner_cls))

_attach_constructors()
