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

from dataclasses import dataclass
from dataclasses import fields as dc_fields

from .acronym import Acronym
from .game_mod_kind import GameModKind


class _ModBase:
    _ACRONYM: str = ""
    _DESC: str = ""
    _KIND: GameModKind = GameModKind.System
    _BITS: int | None = None
    _INCOMPATIBLE: list[str] = []

    @classmethod
    def acronym(cls) -> Acronym:
        return Acronym(cls._ACRONYM)

    @classmethod
    def description(cls) -> str:
        return cls._DESC

    @classmethod
    def kind(cls) -> GameModKind:
        return cls._KIND

    @classmethod
    def bits(cls) -> int | None:
        return cls._BITS

    @classmethod
    def incompatible_mods(cls) -> list[Acronym]:
        return [Acronym(a) for a in cls._INCOMPATIBLE]

    def to_simple(self):
        from .game_mod_simple import GameModSimple, SettingSimple

        settings = {}
        for f in dc_fields(self):  # type: ignore[arg-type]
            val = getattr(self, f.name)
            if val is not None:
                if isinstance(val, bool):
                    settings[f.name] = SettingSimple(val)
                elif isinstance(val, float):
                    settings[f.name] = SettingSimple(val)
                elif isinstance(val, str):
                    settings[f.name] = SettingSimple(val)
                else:
                    settings[f.name] = SettingSimple(val)
        return GameModSimple(acronym=Acronym(self._ACRONYM), settings=settings)

    def __repr__(self) -> str:
        cls = type(self)
        parts = []
        for f in dc_fields(self):  # type: ignore[arg-type]
            val = getattr(self, f.name)
            parts.append(f"{f.name}={val!r}")
        args = ", ".join(parts)
        return f"{cls.__name__}({args})"


# OSU
@dataclass
class EasyOsu(_ModBase):
    """Larger circles, more forgiving HP drain, less accuracy required, and extra lives!"""

    retries: float | None = None
    _ACRONYM = "EZ"
    _DESC = "Larger circles, more forgiving HP drain, less accuracy required, and extra lives!"
    _KIND = GameModKind.DifficultyReduction
    _BITS = 2
    _INCOMPATIBLE = ["EZ", "HR", "AC", "DA"]


@dataclass
class NoFailOsu(_ModBase):
    """You can't fail, no matter what."""

    _ACRONYM = "NF"
    _DESC = "You can't fail, no matter what."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 1
    _INCOMPATIBLE = ["NF", "SD", "PF", "AC", "CN"]


@dataclass
class HalfTimeOsu(_ModBase):
    """Less zoom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "HT"
    _DESC = "Less zoom..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 256
    _INCOMPATIBLE = ["HT", "DC", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class DaycoreOsu(_ModBase):
    """Whoaaaaa..."""

    speed_change: float | None = None
    _ACRONYM = "DC"
    _DESC = "Whoaaaaa..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["DC", "HT", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class HardRockOsu(_ModBase):
    """Everything just got a bit harder..."""

    _ACRONYM = "HR"
    _DESC = "Everything just got a bit harder..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16
    _INCOMPATIBLE = ["HR", "EZ", "DA", "MR"]


@dataclass
class SuddenDeathOsu(_ModBase):
    """Miss and fail."""

    fail_on_slider_tail: bool | None = None
    restart: bool | None = None
    _ACRONYM = "SD"
    _DESC = "Miss and fail."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 32
    _INCOMPATIBLE = ["SD", "NF", "PF", "TP", "CN"]


@dataclass
class PerfectOsu(_ModBase):
    """SS or quit."""

    restart: bool | None = None
    _ACRONYM = "PF"
    _DESC = "SS or quit."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16416
    _INCOMPATIBLE = ["PF", "NF", "SD", "AC", "CN"]


@dataclass
class DoubleTimeOsu(_ModBase):
    """Zoooooooooom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "DT"
    _DESC = "Zoooooooooom..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 64
    _INCOMPATIBLE = ["DT", "HT", "DC", "NC", "WU", "WD", "AS"]


@dataclass
class NightcoreOsu(_ModBase):
    """Uguuuuuuuu..."""

    speed_change: float | None = None
    _ACRONYM = "NC"
    _DESC = "Uguuuuuuuu..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 576
    _INCOMPATIBLE = ["NC", "HT", "DC", "DT", "WU", "WD", "AS"]


@dataclass
class HiddenOsu(_ModBase):
    """Play with no approach circles and fading circles/sliders."""

    only_fade_approach_circles: bool | None = None
    _ACRONYM = "HD"
    _DESC = "Play with no approach circles and fading circles/sliders."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 8
    _INCOMPATIBLE = ["HD", "TC", "SI", "AD", "FR", "DP"]


@dataclass
class TraceableOsu(_ModBase):
    """Put your faith in the approach circles..."""

    _ACRONYM = "TC"
    _DESC = "Put your faith in the approach circles..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["TC", "HD", "TP", "SI", "GR", "DF", "DP"]


@dataclass
class FlashlightOsu(_ModBase):
    """Restricted view area."""

    follow_delay: float | None = None
    size_multiplier: float | None = None
    combo_based_size: bool | None = None
    _ACRONYM = "FL"
    _DESC = "Restricted view area."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 1024
    _INCOMPATIBLE = ["FL", "BL", "BM"]


@dataclass
class BlindsOsu(_ModBase):
    """Play with blinds on your screen."""

    _ACRONYM = "BL"
    _DESC = "Play with blinds on your screen."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["BL", "FL"]


@dataclass
class StrictTrackingOsu(_ModBase):
    """Once you start a slider, follow precisely or get a miss."""

    _ACRONYM = "ST"
    _DESC = "Once you start a slider, follow precisely or get a miss."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["ST", "TP", "CL"]


@dataclass
class AccuracyChallengeOsu(_ModBase):
    """Fail if your accuracy drops too low!"""

    minimum_accuracy: float | None = None
    accuracy_judge_mode: str | None = None
    restart: bool | None = None
    _ACRONYM = "AC"
    _DESC = "Fail if your accuracy drops too low!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["AC", "EZ", "NF", "PF", "CN"]


@dataclass
class TargetPracticeOsu(_ModBase):
    """Practice keeping up with the beat of the song."""

    seed: float | None = None
    metronome: bool | None = None
    _ACRONYM = "TP"
    _DESC = "Practice keeping up with the beat of the song."
    _KIND = GameModKind.Conversion
    _BITS = 8388608
    _INCOMPATIBLE = ["TP", "SD", "TC", "ST", "DA", "RD", "SO", "AD", "DP"]


@dataclass
class DifficultyAdjustOsu(_ModBase):
    """Override a beatmap's difficulty settings."""

    circle_size: float | None = None
    approach_rate: float | None = None
    drain_rate: float | None = None
    overall_difficulty: float | None = None
    extended_limits: bool | None = None
    _ACRONYM = "DA"
    _DESC = "Override a beatmap's difficulty settings."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["DA", "EZ", "HR", "TP"]


@dataclass
class ClassicOsu(_ModBase):
    """Feeling nostalgic?"""

    no_slider_head_accuracy: bool | None = None
    classic_note_lock: bool | None = None
    always_play_tail_sample: bool | None = None
    fade_hit_circle_early: bool | None = None
    classic_health: bool | None = None
    _ACRONYM = "CL"
    _DESC = "Feeling nostalgic?"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CL", "ST"]


@dataclass
class RandomOsu(_ModBase):
    """It never gets boring!"""

    angle_sharpness: float | None = None
    seed: float | None = None
    _ACRONYM = "RD"
    _DESC = "It never gets boring!"
    _KIND = GameModKind.Conversion
    _BITS = 2097152
    _INCOMPATIBLE = ["RD", "TP"]


@dataclass
class MirrorOsu(_ModBase):
    """Flip objects on the chosen axes."""

    reflection: str | None = None
    _ACRONYM = "MR"
    _DESC = "Flip objects on the chosen axes."
    _KIND = GameModKind.Conversion
    _BITS = 1073741824
    _INCOMPATIBLE = ["MR", "HR"]


@dataclass
class AlternateOsu(_ModBase):
    """Don't use the same key twice in a row!"""

    _ACRONYM = "AL"
    _DESC = "Don't use the same key twice in a row!"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["AL", "SG", "AT", "CN", "RX"]


@dataclass
class SingleTapOsu(_ModBase):
    """You must only use one key!"""

    _ACRONYM = "SG"
    _DESC = "You must only use one key!"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["SG", "AL", "AT", "CN", "RX"]


@dataclass
class AutoplayOsu(_ModBase):
    """Watch a perfect automated play through the song."""

    _ACRONYM = "AT"
    _DESC = "Watch a perfect automated play through the song."
    _KIND = GameModKind.Automation
    _BITS = 2048
    _INCOMPATIBLE = ["AT", "AL", "SG", "CN", "RX", "AP", "SO", "MG", "RP", "AS", "TD"]


@dataclass
class CinemaOsu(_ModBase):
    """Watch the video without visual distractions."""

    _ACRONYM = "CN"
    _DESC = "Watch the video without visual distractions."
    _KIND = GameModKind.Automation
    _BITS = 4194304
    _INCOMPATIBLE = [
        "CN",
        "NF",
        "SD",
        "PF",
        "AC",
        "AL",
        "SG",
        "AT",
        "RX",
        "AP",
        "SO",
        "MG",
        "RP",
        "AS",
        "TD",
    ]


@dataclass
class RelaxOsu(_ModBase):
    """You don't need to click. Give your clicking/tapping fingers a break from the heat of things."""

    _ACRONYM = "RX"
    _DESC = "You don't need to click. Give your clicking/tapping fingers a break from the heat of things."
    _KIND = GameModKind.Automation
    _BITS = 128
    _INCOMPATIBLE = ["RX", "AL", "SG", "AT", "CN", "AP", "MG"]


@dataclass
class AutopilotOsu(_ModBase):
    """Automatic cursor movement - just follow the rhythm."""

    _ACRONYM = "AP"
    _DESC = "Automatic cursor movement - just follow the rhythm."
    _KIND = GameModKind.Automation
    _BITS = 8192
    _INCOMPATIBLE = ["AP", "AT", "CN", "RX", "SO", "MG", "RP", "TD"]


@dataclass
class SpunOutOsu(_ModBase):
    """Spinners will be automatically completed."""

    _ACRONYM = "SO"
    _DESC = "Spinners will be automatically completed."
    _KIND = GameModKind.Automation
    _BITS = 4096
    _INCOMPATIBLE = ["SO", "AP", "AT", "CN", "TP"]


@dataclass
class TransformOsu(_ModBase):
    """Everything rotates. EVERYTHING."""

    _ACRONYM = "TR"
    _DESC = "Everything rotates. EVERYTHING."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["TR", "DP", "FR", "MG", "RP", "WG"]


@dataclass
class WiggleOsu(_ModBase):
    """They just won't stay still..."""

    strength: float | None = None
    _ACRONYM = "WG"
    _DESC = "They just won't stay still..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WG", "DP", "MG", "RP", "TR"]


@dataclass
class SpinInOsu(_ModBase):
    """Circles spin in. No approach circles."""

    _ACRONYM = "SI"
    _DESC = "Circles spin in. No approach circles."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["SI", "AD", "DF", "DP", "GR", "HD", "TC"]


@dataclass
class GrowOsu(_ModBase):
    """Hit them at the right size!"""

    start_scale: float | None = None
    _ACRONYM = "GR"
    _DESC = "Hit them at the right size!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["GR", "AD", "DF", "DP", "SI", "TC"]


@dataclass
class DeflateOsu(_ModBase):
    """Hit them at the right size!"""

    start_scale: float | None = None
    _ACRONYM = "DF"
    _DESC = "Hit them at the right size!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["DF", "AD", "GR", "SI", "TC", "DP"]


@dataclass
class WindUpOsu(_ModBase):
    """Can you keep up?"""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WU"
    _DESC = "Can you keep up?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WU", "HT", "DC", "DT", "NC", "WD", "AS"]


@dataclass
class WindDownOsu(_ModBase):
    """Sloooow doooown..."""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WD"
    _DESC = "Sloooow doooown..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WD", "HT", "DC", "DT", "NC", "WU", "AS"]


@dataclass
class BarrelRollOsu(_ModBase):
    """The whole playfield rotates constantly!"""

    spin_speed: float | None = None
    direction: str | None = None
    _ACRONYM = "BR"
    _DESC = "The whole playfield is on a wheel!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["BR", "BU"]


@dataclass
class ApproachDifferentOsu(_ModBase):
    """Never trust the approach circles..."""

    scale: float | None = None
    style: str | None = None
    _ACRONYM = "AD"
    _DESC = "Never trust the approach circles..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["AD", "HD", "DF", "GR", "SI", "FR", "TP"]


@dataclass
class MutedOsu(_ModBase):
    """Can you still feel the rhythm without music?"""

    inverse_muting: bool | None = None
    enable_metronome: bool | None = None
    mute_combo_count: float | None = None
    affects_hit_sounds: bool | None = None
    _ACRONYM = "MU"
    _DESC = "Can you still feel the rhythm without music?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MU"]


@dataclass
class NoScopeOsu(_ModBase):
    """Where's the cursor?"""

    hidden_combo_count: float | None = None
    _ACRONYM = "NS"
    _DESC = "Where's the cursor?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["NS", "BM"]


@dataclass
class MagnetisedOsu(_ModBase):
    """Spooky. The cursor is being pulled towards circles!"""

    attraction_strength: float | None = None
    _ACRONYM = "MG"
    _DESC = "No need to chase the circles – your cursor is a magnet!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MG", "AP", "AT", "BU", "CN", "DP", "RP", "RX", "TR", "WG"]


@dataclass
class RepelOsu(_ModBase):
    """Beware of the circles. They are out to get you!"""

    repulsion_strength: float | None = None
    _ACRONYM = "RP"
    _DESC = "Hit objects run away!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["RP", "AP", "AT", "BU", "CN", "DP", "MG", "TR", "WG"]


@dataclass
class AdaptiveSpeedOsu(_ModBase):
    """The speed adapts to you!"""

    initial_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "AS"
    _DESC = "Let track speed adapt to you."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["AS", "HT", "DC", "DT", "NC", "AT", "CN", "WU", "WD"]


@dataclass
class FreezeFrameOsu(_ModBase):
    """Freeze the background tracks. Only the hit objects will move!"""

    _ACRONYM = "FR"
    _DESC = "Burn the notes into your memory."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["FR", "HD", "AD", "DP", "TR"]


@dataclass
class BubblesOsu(_ModBase):
    """Feeling bubbly?"""

    _ACRONYM = "BU"
    _DESC = "Don't let their popping distract you!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["BU", "BR", "MG", "RP"]


@dataclass
class SynesthesiaOsu(_ModBase):
    """Colour and music weaved together."""

    _ACRONYM = "SY"
    _DESC = "Colours hit objects based on the rhythm."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["SY"]


@dataclass
class DepthOsu(_ModBase):
    """3D. Bam."""

    max_depth: float | None = None
    show_approach_circles: bool | None = None
    _ACRONYM = "DP"
    _DESC = "3D. Almost."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = [
        "DP",
        "HD",
        "TC",
        "TP",
        "TR",
        "WG",
        "SI",
        "GR",
        "DF",
        "MG",
        "RP",
        "FR",
    ]


@dataclass
class BloomOsu(_ModBase):
    """The cursor blooms with spectacular colours!"""

    max_cursor_size: float | None = None
    max_size_combo_count: float | None = None
    _ACRONYM = "BM"
    _DESC = "The cursor blooms into.. a larger cursor!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["BM", "FL", "NS", "TD"]


@dataclass
class TouchDeviceOsu(_ModBase):
    """Automatically applied to plays on devices with a touchscreen."""

    _ACRONYM = "TD"
    _DESC = "Automatically applied to plays on devices with a touchscreen."
    _KIND = GameModKind.System
    _BITS = 4
    _INCOMPATIBLE = ["TD", "AP", "AT", "BM", "CN"]


@dataclass
class ScoreV2Osu(_ModBase):
    """Try scoring under the new scoring system."""

    _ACRONYM = "SV2"
    _DESC = "Score set on earlier osu! versions with the V2 scoring algorithm active."
    _KIND = GameModKind.System
    _BITS = 536870912
    _INCOMPATIBLE = ["SV2"]


# TAIKO mods
@dataclass
class EasyTaiko(_ModBase):
    """Larger notes, more forgiving HP drain, less accuracy required, and extra lives!"""

    retries: float | None = None
    _ACRONYM = "EZ"
    _DESC = "Beats move slower, and less accuracy required!"
    _KIND = GameModKind.DifficultyReduction
    _BITS = 2
    _INCOMPATIBLE = ["EZ", "HR", "DA"]


@dataclass
class NoFailTaiko(_ModBase):
    """You can't fail, no matter what."""

    _ACRONYM = "NF"
    _DESC = "You can't fail, no matter what."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 1
    _INCOMPATIBLE = ["NF", "SD", "PF", "AC", "CN"]


@dataclass
class HalfTimeTaiko(_ModBase):
    """Less zoom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "HT"
    _DESC = "Less zoom..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 256
    _INCOMPATIBLE = ["HT", "DC", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class DaycoreTaiko(_ModBase):
    """Whoaaaaa..."""

    speed_change: float | None = None
    _ACRONYM = "DC"
    _DESC = "Whoaaaaa..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["DC", "HT", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class SimplifiedRhythmTaiko(_ModBase):
    """Simplified rhythm notes for beginner players."""

    one_third_conversion: bool | None = None
    one_sixth_conversion: bool | None = None
    one_eighth_conversion: bool | None = None
    _ACRONYM = "SR"
    _DESC = "Simplify tricky rhythms!"
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["SR"]


@dataclass
class HardRockTaiko(_ModBase):
    """Everything just got a bit harder..."""

    _ACRONYM = "HR"
    _DESC = "Everything just got a bit harder..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16
    _INCOMPATIBLE = ["HR", "EZ", "DA"]


@dataclass
class SuddenDeathTaiko(_ModBase):
    """Miss and fail."""

    restart: bool | None = None
    _ACRONYM = "SD"
    _DESC = "Miss and fail."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 32
    _INCOMPATIBLE = ["SD", "NF", "PF", "CN"]


@dataclass
class PerfectTaiko(_ModBase):
    """SS or quit."""

    restart: bool | None = None
    _ACRONYM = "PF"
    _DESC = "SS or quit."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16416
    _INCOMPATIBLE = ["PF", "NF", "SD", "AC", "CN"]


@dataclass
class DoubleTimeTaiko(_ModBase):
    """Zoooooooooom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "DT"
    _DESC = "Zoooooooooom..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 64
    _INCOMPATIBLE = ["DT", "HT", "DC", "NC", "WU", "WD", "AS"]


@dataclass
class NightcoreTaiko(_ModBase):
    """Uguuuuuuuu..."""

    speed_change: float | None = None
    _ACRONYM = "NC"
    _DESC = "Uguuuuuuuu..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 576
    _INCOMPATIBLE = ["NC", "HT", "DC", "DT", "WU", "WD", "AS"]


@dataclass
class HiddenTaiko(_ModBase):
    """The notes fade out before you hit them!"""

    _ACRONYM = "HD"
    _DESC = "Beats fade out before you hit them!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 8
    _INCOMPATIBLE = ["HD"]


@dataclass
class FlashlightTaiko(_ModBase):
    """Restricted view area."""

    follow_delay: float | None = None
    size_multiplier: float | None = None
    combo_based_size: bool | None = None
    _ACRONYM = "FL"
    _DESC = "Restricted view area."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 1024
    _INCOMPATIBLE = ["FL"]


@dataclass
class AccuracyChallengeTaiko(_ModBase):
    """Fail if your accuracy drops too low!"""

    minimum_accuracy: float | None = None
    accuracy_judge_mode: str | None = None
    restart: bool | None = None
    _ACRONYM = "AC"
    _DESC = "Fail if your accuracy drops too low!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["AC", "NF", "PF", "CN"]


@dataclass
class RandomTaiko(_ModBase):
    """Shuffle around the colours!"""

    seed: float | None = None
    _ACRONYM = "RD"
    _DESC = "Shuffle around the colours!"
    _KIND = GameModKind.Conversion
    _BITS = 2097152
    _INCOMPATIBLE = ["RD", "SW"]


@dataclass
class DifficultyAdjustTaiko(_ModBase):
    """Override a beatmap's difficulty settings."""

    scroll_speed: float | None = None
    drain_rate: float | None = None
    overall_difficulty: float | None = None
    extended_limits: bool | None = None
    _ACRONYM = "DA"
    _DESC = "Override a beatmap's difficulty settings."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["DA", "EZ", "HR"]


@dataclass
class ClassicTaiko(_ModBase):
    """The classic osu!taiko experience."""

    classic_note_lock: bool | None = None
    _ACRONYM = "CL"
    _DESC = "The classic osu!taiko experience."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CL"]


@dataclass
class SwapTaiko(_ModBase):
    """Dons become kats, kats become dons."""

    _ACRONYM = "SW"
    _DESC = "Dons become kats, kats become dons"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["SW", "RD"]


@dataclass
class SingleTapTaiko(_ModBase):
    """One key for dons, one key for kats."""

    _ACRONYM = "SG"
    _DESC = "One key for dons, one key for kats."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["SG", "AT", "CN", "RX"]


@dataclass
class ConstantSpeedTaiko(_ModBase):
    """No more tricky speed changes!"""

    _ACRONYM = "CS"
    _DESC = "No more tricky speed changes!"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CS"]


@dataclass
class AutoplayTaiko(_ModBase):
    """Watch a perfect automated play through the song."""

    _ACRONYM = "AT"
    _DESC = "Watch a perfect automated play through the song."
    _KIND = GameModKind.Automation
    _BITS = 2048
    _INCOMPATIBLE = ["AT", "SG", "CN", "RX", "AS"]


@dataclass
class CinemaTaiko(_ModBase):
    """Watch the video without visual distractions."""

    _ACRONYM = "CN"
    _DESC = "Watch the video without visual distractions."
    _KIND = GameModKind.Automation
    _BITS = 4194304
    _INCOMPATIBLE = ["CN", "NF", "SD", "PF", "AC", "SG", "AT", "RX", "AS"]


@dataclass
class RelaxTaiko(_ModBase):
    """You don't need to drum. Use the autoplay cursor to guide your aim."""

    _ACRONYM = "RX"
    _DESC = "No need to remember which key is correct anymore!"
    _KIND = GameModKind.Automation
    _BITS = 128
    _INCOMPATIBLE = ["RX", "AT", "CN", "SG"]


@dataclass
class WindUpTaiko(_ModBase):
    """Can you keep up?"""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WU"
    _DESC = "Can you keep up?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WU", "HT", "DC", "DT", "NC", "WD", "AS"]


@dataclass
class WindDownTaiko(_ModBase):
    """Sloooow doooown..."""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WD"
    _DESC = "Sloooow doooown..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WD", "HT", "DC", "DT", "NC", "WU", "AS"]


@dataclass
class MutedTaiko(_ModBase):
    """Can you still feel the rhythm without music?"""

    inverse_muting: bool | None = None
    enable_metronome: bool | None = None
    mute_combo_count: float | None = None
    affects_hit_sounds: bool | None = None
    _ACRONYM = "MU"
    _DESC = "Can you still feel the rhythm without music?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MU"]


@dataclass
class AdaptiveSpeedTaiko(_ModBase):
    """The speed adapts to you!"""

    initial_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "AS"
    _DESC = "Let track speed adapt to you."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["AS", "HT", "DC", "DT", "NC", "AT", "CN", "WU", "WD"]


@dataclass
class ScoreV2Taiko(_ModBase):
    """Try scoring under the new scoring system."""

    _ACRONYM = "SV2"
    _DESC = "Score set on earlier osu! versions with the V2 scoring algorithm active."
    _KIND = GameModKind.System
    _BITS = 536870912
    _INCOMPATIBLE = ["SV2"]


# CATCH mods
@dataclass
class EasyCatch(_ModBase):
    """Larger fruits, more forgiving HP drain, less accuracy required, and extra lives!"""

    retries: float | None = None
    _ACRONYM = "EZ"
    _DESC = "Larger fruits, more forgiving HP drain, less accuracy required, and extra lives!"
    _KIND = GameModKind.DifficultyReduction
    _BITS = 2
    _INCOMPATIBLE = ["EZ", "HR", "AC", "DA"]


@dataclass
class NoFailCatch(_ModBase):
    """You can't fail, no matter what."""

    _ACRONYM = "NF"
    _DESC = "You can't fail, no matter what."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 1
    _INCOMPATIBLE = ["NF", "SD", "PF", "AC", "CN"]


@dataclass
class HalfTimeCatch(_ModBase):
    """Less zoom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "HT"
    _DESC = "Less zoom..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 256
    _INCOMPATIBLE = ["HT", "DC", "DT", "NC", "WU", "WD"]


@dataclass
class DaycoreCatch(_ModBase):
    """Whoaaaaa..."""

    speed_change: float | None = None
    _ACRONYM = "DC"
    _DESC = "Whoaaaaa..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["DC", "HT", "DT", "NC", "WU", "WD"]


@dataclass
class HardRockCatch(_ModBase):
    """Everything just got a bit harder..."""

    _ACRONYM = "HR"
    _DESC = "Everything just got a bit harder..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16
    _INCOMPATIBLE = ["HR", "EZ", "DA"]


@dataclass
class SuddenDeathCatch(_ModBase):
    """Miss and fail."""

    restart: bool | None = None
    _ACRONYM = "SD"
    _DESC = "Miss and fail."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 32
    _INCOMPATIBLE = ["SD", "NF", "PF", "CN"]


@dataclass
class PerfectCatch(_ModBase):
    """SS or quit."""

    restart: bool | None = None
    _ACRONYM = "PF"
    _DESC = "SS or quit."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16416
    _INCOMPATIBLE = ["PF", "NF", "SD", "AC", "CN"]


@dataclass
class DoubleTimeCatch(_ModBase):
    """Zoooooooooom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "DT"
    _DESC = "Zoooooooooom..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 64
    _INCOMPATIBLE = ["DT", "HT", "DC", "NC", "WU", "WD"]


@dataclass
class NightcoreCatch(_ModBase):
    """Uguuuuuuuu..."""

    speed_change: float | None = None
    _ACRONYM = "NC"
    _DESC = "Uguuuuuuuu..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 576
    _INCOMPATIBLE = ["NC", "HT", "DC", "DT", "WU", "WD"]


@dataclass
class HiddenCatch(_ModBase):
    """Play with fading fruits."""

    _ACRONYM = "HD"
    _DESC = "Play with fading fruits."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 8
    _INCOMPATIBLE = ["HD"]


@dataclass
class FlashlightCatch(_ModBase):
    """Restricted view area."""

    follow_delay: float | None = None
    size_multiplier: float | None = None
    combo_based_size: bool | None = None
    _ACRONYM = "FL"
    _DESC = "Restricted view area."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 1024
    _INCOMPATIBLE = ["FL"]


@dataclass
class AccuracyChallengeCatch(_ModBase):
    """Fail if your accuracy drops too low!"""

    minimum_accuracy: float | None = None
    accuracy_judge_mode: str | None = None
    restart: bool | None = None
    _ACRONYM = "AC"
    _DESC = "Fail if your accuracy drops too low!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["AC", "EZ", "NF", "PF", "CN"]


@dataclass
class DifficultyAdjustCatch(_ModBase):
    """Override a beatmap's difficulty settings."""

    circle_size: float | None = None
    approach_rate: float | None = None
    drain_rate: float | None = None
    overall_difficulty: float | None = None
    extended_limits: bool | None = None
    hard_rock_offsets: bool | None = None
    _ACRONYM = "DA"
    _DESC = "Override a beatmap's difficulty settings."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["DA", "EZ", "HR"]


@dataclass
class ClassicCatch(_ModBase):
    """Feeling nostalgic?"""

    _ACRONYM = "CL"
    _DESC = "Feeling nostalgic?"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CL"]


@dataclass
class MirrorCatch(_ModBase):
    """Mirror the playfield."""

    _ACRONYM = "MR"
    _DESC = "Fruits are flipped horizontally."
    _KIND = GameModKind.Conversion
    _BITS = 1073741824
    _INCOMPATIBLE = ["MR"]


@dataclass
class AutoplayCatch(_ModBase):
    """Watch a perfect automated play through the song."""

    _ACRONYM = "AT"
    _DESC = "Watch a perfect automated play through the song."
    _KIND = GameModKind.Automation
    _BITS = 2048
    _INCOMPATIBLE = ["AT", "CN", "RX", "MF"]


@dataclass
class CinemaCatch(_ModBase):
    """Watch the video without visual distractions."""

    _ACRONYM = "CN"
    _DESC = "Watch the video without visual distractions."
    _KIND = GameModKind.Automation
    _BITS = 4194304
    _INCOMPATIBLE = ["CN", "NF", "SD", "PF", "AC", "AT", "RX", "MF"]


@dataclass
class RelaxCatch(_ModBase):
    """Use the mouse to control the catcher."""

    _ACRONYM = "RX"
    _DESC = "Use the mouse to control the catcher."
    _KIND = GameModKind.Automation
    _BITS = 128
    _INCOMPATIBLE = ["RX", "AT", "CN", "MF"]


@dataclass
class WindUpCatch(_ModBase):
    """Can you keep up?"""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WU"
    _DESC = "Can you keep up?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WU", "HT", "DC", "DT", "NC", "WD"]


@dataclass
class WindDownCatch(_ModBase):
    """Sloooow doooown..."""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WD"
    _DESC = "Sloooow doooown..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WD", "HT", "DC", "DT", "NC", "WU"]


@dataclass
class FloatingFruitsCatch(_ModBase):
    """The fruits are coming in from different heights."""

    _ACRONYM = "FF"
    _DESC = "The fruits are... floating?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["FF"]


@dataclass
class MutedCatch(_ModBase):
    """Can you still feel the rhythm without music?"""

    inverse_muting: bool | None = None
    enable_metronome: bool | None = None
    mute_combo_count: float | None = None
    affects_hit_sounds: bool | None = None
    _ACRONYM = "MU"
    _DESC = "Can you still feel the rhythm without music?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MU"]


@dataclass
class NoScopeCatch(_ModBase):
    """Where is the catcher?"""

    hidden_combo_count: float | None = None
    _ACRONYM = "NS"
    _DESC = "Where's the catcher?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["NS"]


@dataclass
class MovingFastCatch(_ModBase):
    """You'll never walk alone. Unless you don't walk at all."""

    _ACRONYM = "MF"
    _DESC = "Dashing by default, slow down!"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MF", "AT", "CN", "RX"]


@dataclass
class ScoreV2Catch(_ModBase):
    """Try scoring under the new scoring system."""

    _ACRONYM = "SV2"
    _DESC = "Score set on earlier osu! versions with the V2 scoring algorithm active."
    _KIND = GameModKind.System
    _BITS = 536870912
    _INCOMPATIBLE = ["SV2"]


# MANIA mods
@dataclass
class EasyMania(_ModBase):
    """Larger notes, more forgiving HP drain, less accuracy required, and extra lives!"""

    retries: float | None = None
    _ACRONYM = "EZ"
    _DESC = "More forgiving HP drain, less accuracy required, and extra lives!"
    _KIND = GameModKind.DifficultyReduction
    _BITS = 2
    _INCOMPATIBLE = ["EZ", "HR", "AC", "DA"]


@dataclass
class NoFailMania(_ModBase):
    """You can't fail, no matter what."""

    _ACRONYM = "NF"
    _DESC = "You can't fail, no matter what."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 1
    _INCOMPATIBLE = ["NF", "SD", "PF", "AC", "CN"]


@dataclass
class HalfTimeMania(_ModBase):
    """Less zoom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "HT"
    _DESC = "Less zoom..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = 256
    _INCOMPATIBLE = ["HT", "DC", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class DaycoreMania(_ModBase):
    """Whoaaaaa..."""

    speed_change: float | None = None
    _ACRONYM = "DC"
    _DESC = "Whoaaaaa..."
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["DC", "HT", "DT", "NC", "WU", "WD", "AS"]


@dataclass
class NoReleaseMania(_ModBase):
    """Hold the keys. Do not release them!"""

    _ACRONYM = "NR"
    _DESC = "No more timing the end of hold notes."
    _KIND = GameModKind.DifficultyReduction
    _BITS = None
    _INCOMPATIBLE = ["NR", "HO"]


@dataclass
class HardRockMania(_ModBase):
    """Everything just got a bit harder..."""

    _ACRONYM = "HR"
    _DESC = "Everything just got a bit harder..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16
    _INCOMPATIBLE = ["HR", "EZ", "DA"]


@dataclass
class SuddenDeathMania(_ModBase):
    """Miss and fail."""

    restart: bool | None = None
    _ACRONYM = "SD"
    _DESC = "Miss and fail."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 32
    _INCOMPATIBLE = ["SD", "NF", "PF", "CN"]


@dataclass
class PerfectMania(_ModBase):
    """SS or quit."""

    restart: bool | None = None
    require_perfect_hits: bool | None = None
    _ACRONYM = "PF"
    _DESC = "SS or quit."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 16416
    _INCOMPATIBLE = ["PF", "NF", "SD", "AC", "CN"]


@dataclass
class DoubleTimeMania(_ModBase):
    """Zoooooooooom..."""

    speed_change: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "DT"
    _DESC = "Zoooooooooom..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 64
    _INCOMPATIBLE = ["DT", "HT", "DC", "NC", "WU", "WD", "AS"]


@dataclass
class NightcoreMania(_ModBase):
    """Uguuuuuuuu..."""

    speed_change: float | None = None
    _ACRONYM = "NC"
    _DESC = "Uguuuuuuuu..."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 576
    _INCOMPATIBLE = ["NC", "HT", "DC", "DT", "WU", "WD", "AS"]


@dataclass
class FadeInMania(_ModBase):
    """The notes fade in from the bottom of the playfield."""

    coverage: float | None = None
    _ACRONYM = "FI"
    _DESC = "Keys appear out of nowhere!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 1048576
    _INCOMPATIBLE = ["FI", "CO", "HD", "FL"]


@dataclass
class HiddenMania(_ModBase):
    """The notes fade out before you hit them!"""

    coverage: float | None = None
    _ACRONYM = "HD"
    _DESC = "Keys fade out before you hit them!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 8
    _INCOMPATIBLE = ["HD", "CO", "FI", "FL"]


@dataclass
class CoverMania(_ModBase):
    """A portion of the playfield is hidden."""

    coverage: float | None = None
    direction: str | None = None
    _ACRONYM = "CO"
    _DESC = "Decrease the playfield's viewing area."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["CO", "FI", "HD", "FL"]


@dataclass
class FlashlightMania(_ModBase):
    """Restricted view area."""

    follow_delay: float | None = None
    size_multiplier: float | None = None
    combo_based_size: bool | None = None
    _ACRONYM = "FL"
    _DESC = "Restricted view area."
    _KIND = GameModKind.DifficultyIncrease
    _BITS = 1024
    _INCOMPATIBLE = ["FL", "CO", "FI", "HD"]


@dataclass
class AccuracyChallengeMania(_ModBase):
    """Fail if your accuracy drops too low!"""

    minimum_accuracy: float | None = None
    accuracy_judge_mode: str | None = None
    restart: bool | None = None
    _ACRONYM = "AC"
    _DESC = "Fail if your accuracy drops too low!"
    _KIND = GameModKind.DifficultyIncrease
    _BITS = None
    _INCOMPATIBLE = ["AC", "EZ", "NF", "PF", "CN"]


@dataclass
class RandomMania(_ModBase):
    """Shuffle around the notes!"""

    seed: float | None = None
    _ACRONYM = "RD"
    _DESC = "Shuffle around the keys!"
    _KIND = GameModKind.Conversion
    _BITS = 2097152
    _INCOMPATIBLE = ["RD"]


@dataclass
class DualStagesMania(_ModBase):
    """Double the stages. Double the fun!"""

    _ACRONYM = "DS"
    _DESC = "Double the stages, double the fun!"
    _KIND = GameModKind.Conversion
    _BITS = 33554432
    _INCOMPATIBLE = ["DS"]


@dataclass
class MirrorMania(_ModBase):
    """Mirror the notes on the chosen axes."""

    reflection: str | None = None
    _ACRONYM = "MR"
    _DESC = "Notes are flipped horizontally."
    _KIND = GameModKind.Conversion
    _BITS = 1073741824
    _INCOMPATIBLE = ["MR"]


@dataclass
class DifficultyAdjustMania(_ModBase):
    """Override a beatmap's difficulty settings."""

    drain_rate: float | None = None
    overall_difficulty: float | None = None
    extended_limits: bool | None = None
    _ACRONYM = "DA"
    _DESC = "Override a beatmap's difficulty settings."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["DA", "EZ", "HR"]


@dataclass
class ClassicMania(_ModBase):
    """Feeling nostalgic?"""

    classic_health: bool | None = None
    _ACRONYM = "CL"
    _DESC = "Feeling nostalgic?"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CL"]


@dataclass
class InvertMania(_ModBase):
    """Hold. Don't click."""

    _ACRONYM = "IN"
    _DESC = "Hold the keys. To the beat."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["IN", "HO"]


@dataclass
class ConstantSpeedMania(_ModBase):
    """No more tricky speed changes!"""

    _ACRONYM = "CS"
    _DESC = "No more tricky speed changes!"
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["CS"]


@dataclass
class HoldOffMania(_ModBase):
    """No more holds, only notes!"""

    _ACRONYM = "HO"
    _DESC = "Replaces all hold notes with normal notes."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["HO", "NR", "IN"]


@dataclass
class OneKeyMania(_ModBase):
    """One key to tap them all!"""

    _ACRONYM = "1K"
    _DESC = "Play with one key."
    _KIND = GameModKind.Conversion
    _BITS = 67108864
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class TwoKeysMania(_ModBase):
    """Two keys to tap them all!"""

    _ACRONYM = "2K"
    _DESC = "Play with two keys."
    _KIND = GameModKind.Conversion
    _BITS = 268435456
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class ThreeKeysMania(_ModBase):
    """Three keys to tap them all!"""

    _ACRONYM = "3K"
    _DESC = "Play with three keys."
    _KIND = GameModKind.Conversion
    _BITS = 134217728
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class FourKeysMania(_ModBase):
    """Four keys to tap them all!"""

    _ACRONYM = "4K"
    _DESC = "Play with four keys."
    _KIND = GameModKind.Conversion
    _BITS = 32768
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class FiveKeysMania(_ModBase):
    """Five keys to tap them all!"""

    _ACRONYM = "5K"
    _DESC = "Play with five keys."
    _KIND = GameModKind.Conversion
    _BITS = 65536
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class SixKeysMania(_ModBase):
    """Six keys to tap them all!"""

    _ACRONYM = "6K"
    _DESC = "Play with six keys."
    _KIND = GameModKind.Conversion
    _BITS = 131072
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class SevenKeysMania(_ModBase):
    """Seven keys to tap them all!"""

    _ACRONYM = "7K"
    _DESC = "Play with seven keys."
    _KIND = GameModKind.Conversion
    _BITS = 262144
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class EightKeysMania(_ModBase):
    """Eight keys to tap them all!"""

    _ACRONYM = "8K"
    _DESC = "Play with eight keys."
    _KIND = GameModKind.Conversion
    _BITS = 524288
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class NineKeysMania(_ModBase):
    """Nine keys to tap them all!"""

    _ACRONYM = "9K"
    _DESC = "Play with nine keys."
    _KIND = GameModKind.Conversion
    _BITS = 16777216
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class TenKeysMania(_ModBase):
    """Ten keys to tap them all!"""

    _ACRONYM = "10K"
    _DESC = "Play with ten keys."
    _KIND = GameModKind.Conversion
    _BITS = None
    _INCOMPATIBLE = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K"]


@dataclass
class AutoplayMania(_ModBase):
    """Watch a perfect automated play through the song."""

    _ACRONYM = "AT"
    _DESC = "Watch a perfect automated play through the song."
    _KIND = GameModKind.Automation
    _BITS = 2048
    _INCOMPATIBLE = ["AT", "CN", "AS"]


@dataclass
class CinemaMania(_ModBase):
    """Watch the video without visual distractions."""

    _ACRONYM = "CN"
    _DESC = "Watch the video without visual distractions."
    _KIND = GameModKind.Automation
    _BITS = 4194304
    _INCOMPATIBLE = ["CN", "NF", "SD", "PF", "AC", "AT", "AS"]


@dataclass
class WindUpMania(_ModBase):
    """Can you keep up?"""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WU"
    _DESC = "Can you keep up?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WU", "HT", "DC", "DT", "NC", "WD", "AS"]


@dataclass
class WindDownMania(_ModBase):
    """Sloooow doooown..."""

    initial_rate: float | None = None
    final_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "WD"
    _DESC = "Sloooow doooown..."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["WD", "HT", "DC", "DT", "NC", "WU", "AS"]


@dataclass
class MutedMania(_ModBase):
    """Can you still feel the rhythm without music?"""

    inverse_muting: bool | None = None
    enable_metronome: bool | None = None
    mute_combo_count: float | None = None
    affects_hit_sounds: bool | None = None
    _ACRONYM = "MU"
    _DESC = "Can you still feel the rhythm without music?"
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["MU"]


@dataclass
class AdaptiveSpeedMania(_ModBase):
    """The speed adapts to you!"""

    initial_rate: float | None = None
    adjust_pitch: bool | None = None
    _ACRONYM = "AS"
    _DESC = "Let track speed adapt to you."
    _KIND = GameModKind.Fun
    _BITS = None
    _INCOMPATIBLE = ["AS", "HT", "DC", "DT", "NC", "AT", "CN", "WU", "WD"]


@dataclass
class ScoreV2Mania(_ModBase):
    """Try scoring under the new scoring system."""

    _ACRONYM = "SV2"
    _DESC = "Score set on earlier osu! versions with the V2 scoring algorithm active."
    _KIND = GameModKind.System
    _BITS = 536870912
    _INCOMPATIBLE = ["SV2"]


# Special
@dataclass
class UnknownMod(_ModBase):
    """A mod not recognised by this library version."""

    acronym_str: str = ""

    UNKNOWN_ACRONYM: str = "??"

    def acronym(self) -> Acronym:  # type: ignore[override]
        s = self.acronym_str if self.acronym_str and self.acronym_str != "??" else "??"
        try:
            return Acronym(s)
        except ValueError:
            return Acronym("EZ")  # fallback

    @classmethod
    def description(cls) -> str:
        return "Unknown mod"

    @classmethod
    def kind(cls) -> GameModKind:
        return GameModKind.System

    @classmethod
    def bits(cls) -> int | None:
        return None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UnknownMod):
            return self.acronym_str == other.acronym_str
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.acronym_str)


# Mode-specific Unknown variants
@dataclass
class UnknownOsu(UnknownMod):
    """Unknown osu! mod."""

    pass


@dataclass
class UnknownTaiko(UnknownMod):
    """Unknown osu!taiko mod."""

    pass


@dataclass
class UnknownCatch(UnknownMod):
    """Unknown osu!catch mod."""

    pass


@dataclass
class UnknownMania(UnknownMod):
    """Unknown osu!mania mod."""

    pass
