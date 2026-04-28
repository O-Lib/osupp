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

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from osupp_mods import (
    AccuracyChallengeCatch,
    AccuracyChallengeMania,
    AccuracyChallengeOsu,
    AccuracyChallengeTaiko,
    Acronym,
    AdaptiveSpeedMania,
    AdaptiveSpeedOsu,
    AdaptiveSpeedTaiko,
    AlternateOsu,
    ApproachDifferentOsu,
    AutopilotOsu,
    AutoplayCatch,
    AutoplayMania,
    AutoplayOsu,
    AutoplayTaiko,
    BarrelRollOsu,
    BlindsOsu,
    BloomOsu,
    BubblesOsu,
    CinemaCatch,
    CinemaMania,
    CinemaOsu,
    CinemaTaiko,
    ClassicCatch,
    ClassicMania,
    ClassicOsu,
    ClassicTaiko,
    ConstantSpeedMania,
    ConstantSpeedTaiko,
    CoverMania,
    DaycoreCatch,
    DaycoreMania,
    DaycoreOsu,
    DaycoreTaiko,
    DeflateOsu,
    DepthOsu,
    DifficultyAdjustCatch,
    DifficultyAdjustMania,
    DifficultyAdjustOsu,
    DifficultyAdjustTaiko,
    DoubleTimeCatch,
    DoubleTimeMania,
    DoubleTimeOsu,
    DoubleTimeTaiko,
    DualStagesMania,
    # All catch mods
    EasyCatch,
    # All mania mods
    EasyMania,
    # All osu! mods
    EasyOsu,
    # All taiko mods
    EasyTaiko,
    EightKeysMania,
    FadeInMania,
    FiveKeysMania,
    FlashlightCatch,
    FlashlightMania,
    FlashlightOsu,
    FlashlightTaiko,
    FloatingFruitsCatch,
    FourKeysMania,
    FreezeFrameOsu,
    GameMod,
    GameMode,
    GameModIntermode,
    GameModKind,
    GameMods,
    GameModSimple,
    GameModsIntermode,
    GameModsLegacy,
    GrowOsu,
    HalfTimeCatch,
    HalfTimeMania,
    HalfTimeOsu,
    HalfTimeTaiko,
    HardRockCatch,
    HardRockMania,
    HardRockOsu,
    HardRockTaiko,
    HiddenCatch,
    HiddenMania,
    HiddenOsu,
    HiddenTaiko,
    HoldOffMania,
    InvertMania,
    MagnetisedOsu,
    MirrorCatch,
    MirrorMania,
    MirrorOsu,
    MovingFastCatch,
    MutedCatch,
    MutedMania,
    MutedOsu,
    MutedTaiko,
    NightcoreCatch,
    NightcoreMania,
    NightcoreOsu,
    NightcoreTaiko,
    NineKeysMania,
    NoFailCatch,
    NoFailMania,
    NoFailOsu,
    NoFailTaiko,
    NoReleaseMania,
    NoScopeCatch,
    NoScopeOsu,
    OneKeyMania,
    PerfectCatch,
    PerfectMania,
    PerfectOsu,
    PerfectTaiko,
    RandomMania,
    RandomOsu,
    RandomTaiko,
    RelaxCatch,
    RelaxOsu,
    RelaxTaiko,
    RepelOsu,
    ScoreV2Catch,
    ScoreV2Mania,
    ScoreV2Osu,
    ScoreV2Taiko,
    SettingSimple,
    SevenKeysMania,
    SimplifiedRhythmTaiko,
    SingleTapOsu,
    SingleTapTaiko,
    SixKeysMania,
    SpinInOsu,
    SpunOutOsu,
    StrictTrackingOsu,
    SuddenDeathCatch,
    SuddenDeathMania,
    SuddenDeathOsu,
    SuddenDeathTaiko,
    SwapTaiko,
    SynesthesiaOsu,
    TargetPracticeOsu,
    TenKeysMania,
    ThreeKeysMania,
    TouchDeviceOsu,
    TraceableOsu,
    TransformOsu,
    TwoKeysMania,
    WiggleOsu,
    WindDownCatch,
    WindDownMania,
    WindDownOsu,
    WindDownTaiko,
    WindUpCatch,
    WindUpMania,
    WindUpOsu,
    WindUpTaiko,
)


# Acronym
class TestAcronym:
    def test_basic(self):
        a = Acronym("HD")
        assert str(a) == "HD"

    def test_equality(self):
        assert Acronym("DT") == Acronym("DT")
        assert Acronym("DT") == "DT"
        assert Acronym("DT") != Acronym("HD")

    def test_invalid(self):
        with pytest.raises(ValueError):
            Acronym("lowercase")

    def test_from_str(self):
        a = Acronym.from_str("dt")
        assert str(a) == "DT"

    def test_hash(self):
        s = {Acronym("HD"), Acronym("DT"), Acronym("HD")}
        assert len(s) == 2


# GameMode
class TestGameMode:
    def test_values(self):
        assert GameMode.Osu == 0
        assert GameMode.Taiko == 1
        assert GameMode.Catch == 2
        assert GameMode.Mania == 3

    def test_str(self):
        assert str(GameMode.Osu) == "osu"
        assert str(GameMode.Catch) == "fruits"

    def test_from_str(self):
        assert GameMode.from_str("taiko") == GameMode.Taiko
        assert GameMode.from_str("1") == GameMode.Taiko
        assert GameMode.from_str("ctb") == GameMode.Catch

    def test_invalid(self):
        with pytest.raises(ValueError):
            GameMode.from_str("invalid")


# GameModKind
class TestGameModKind:
    def test_all_kinds(self):
        kinds = [
            GameModKind.DifficultyReduction,
            GameModKind.DifficultyIncrease,
            GameModKind.Automation,
            GameModKind.Conversion,
            GameModKind.Fun,
            GameModKind.System,
        ]
        assert len(kinds) == 6


# Individual Mod Dataclasses (141)
OSU_MODS = [
    EasyOsu,
    NoFailOsu,
    HalfTimeOsu,
    DaycoreOsu,
    HardRockOsu,
    SuddenDeathOsu,
    PerfectOsu,
    DoubleTimeOsu,
    NightcoreOsu,
    HiddenOsu,
    TraceableOsu,
    FlashlightOsu,
    BlindsOsu,
    StrictTrackingOsu,
    AccuracyChallengeOsu,
    TargetPracticeOsu,
    DifficultyAdjustOsu,
    ClassicOsu,
    RandomOsu,
    MirrorOsu,
    AlternateOsu,
    SingleTapOsu,
    AutoplayOsu,
    CinemaOsu,
    RelaxOsu,
    AutopilotOsu,
    SpunOutOsu,
    TransformOsu,
    WiggleOsu,
    SpinInOsu,
    GrowOsu,
    DeflateOsu,
    WindUpOsu,
    WindDownOsu,
    BarrelRollOsu,
    ApproachDifferentOsu,
    MutedOsu,
    NoScopeOsu,
    MagnetisedOsu,
    RepelOsu,
    AdaptiveSpeedOsu,
    FreezeFrameOsu,
    BubblesOsu,
    SynesthesiaOsu,
    DepthOsu,
    BloomOsu,
    TouchDeviceOsu,
    ScoreV2Osu,
]
TAIKO_MODS = [
    EasyTaiko,
    NoFailTaiko,
    HalfTimeTaiko,
    DaycoreTaiko,
    SimplifiedRhythmTaiko,
    HardRockTaiko,
    SuddenDeathTaiko,
    PerfectTaiko,
    DoubleTimeTaiko,
    NightcoreTaiko,
    HiddenTaiko,
    FlashlightTaiko,
    AccuracyChallengeTaiko,
    RandomTaiko,
    DifficultyAdjustTaiko,
    ClassicTaiko,
    SwapTaiko,
    SingleTapTaiko,
    ConstantSpeedTaiko,
    AutoplayTaiko,
    CinemaTaiko,
    RelaxTaiko,
    WindUpTaiko,
    WindDownTaiko,
    MutedTaiko,
    AdaptiveSpeedTaiko,
    ScoreV2Taiko,
]
CATCH_MODS = [
    EasyCatch,
    NoFailCatch,
    HalfTimeCatch,
    DaycoreCatch,
    HardRockCatch,
    SuddenDeathCatch,
    PerfectCatch,
    DoubleTimeCatch,
    NightcoreCatch,
    HiddenCatch,
    FlashlightCatch,
    AccuracyChallengeCatch,
    DifficultyAdjustCatch,
    ClassicCatch,
    MirrorCatch,
    AutoplayCatch,
    CinemaCatch,
    RelaxCatch,
    WindUpCatch,
    WindDownCatch,
    FloatingFruitsCatch,
    MutedCatch,
    NoScopeCatch,
    MovingFastCatch,
    ScoreV2Catch,
]
MANIA_MODS = [
    EasyMania,
    NoFailMania,
    HalfTimeMania,
    DaycoreMania,
    NoReleaseMania,
    HardRockMania,
    SuddenDeathMania,
    PerfectMania,
    DoubleTimeMania,
    NightcoreMania,
    FadeInMania,
    HiddenMania,
    CoverMania,
    FlashlightMania,
    AccuracyChallengeMania,
    RandomMania,
    DualStagesMania,
    MirrorMania,
    DifficultyAdjustMania,
    ClassicMania,
    InvertMania,
    ConstantSpeedMania,
    HoldOffMania,
    OneKeyMania,
    TwoKeysMania,
    ThreeKeysMania,
    FourKeysMania,
    FiveKeysMania,
    SixKeysMania,
    SevenKeysMania,
    EightKeysMania,
    NineKeysMania,
    TenKeysMania,
    AutoplayMania,
    CinemaMania,
    WindUpMania,
    WindDownMania,
    MutedMania,
    AdaptiveSpeedMania,
    ScoreV2Mania,
]
ALL_MOD_CLASSES = OSU_MODS + TAIKO_MODS + CATCH_MODS + MANIA_MODS


class TestAllModClasses:
    def test_total_count(self):
        assert len(ALL_MOD_CLASSES) == 140

    @pytest.mark.parametrize("mod_cls", ALL_MOD_CLASSES)
    def test_acronym_is_string(self, mod_cls):
        acr = mod_cls.acronym()
        assert isinstance(acr, Acronym)
        assert len(str(acr)) >= 1

    @pytest.mark.parametrize("mod_cls", ALL_MOD_CLASSES)
    def test_description_nonempty(self, mod_cls):
        assert len(mod_cls.description()) > 0

    @pytest.mark.parametrize("mod_cls", ALL_MOD_CLASSES)
    def test_kind_valid(self, mod_cls):
        assert isinstance(mod_cls.kind(), GameModKind)

    @pytest.mark.parametrize("mod_cls", ALL_MOD_CLASSES)
    def test_bits_type(self, mod_cls):
        b = mod_cls.bits()
        assert b is None or isinstance(b, int)

    @pytest.mark.parametrize("mod_cls", ALL_MOD_CLASSES)
    def test_incompatible_mods_list(self, mod_cls):
        incompat = mod_cls.incompatible_mods()
        assert isinstance(incompat, list)
        for a in incompat:
            assert isinstance(a, Acronym)

    def test_specific_mods(self):
        assert str(HiddenOsu.acronym()) == "HD"
        assert HiddenOsu.bits() == 8
        assert HiddenOsu.kind() == GameModKind.DifficultyIncrease

        assert str(NoFailOsu.acronym()) == "NF"
        assert NoFailOsu.bits() == 1
        assert NoFailOsu.kind() == GameModKind.DifficultyReduction

        assert str(DoubleTimeOsu.acronym()) == "DT"
        assert DoubleTimeOsu.bits() == 64

        assert str(FadeInMania.acronym()) == "FI"
        assert FadeInMania.bits() == 1048576

        assert str(TenKeysMania.acronym()) == "10K"
        assert str(ScoreV2Osu.acronym()) == "SV2"
        assert ScoreV2Osu.bits() == 536870912

    def test_fields_default_none(self):
        hd = HiddenOsu()
        assert hd.only_fade_approach_circles is None

        fl = FlashlightOsu()
        assert fl.follow_delay is None
        assert fl.size_multiplier is None
        assert fl.combo_based_size is None

        da = DifficultyAdjustOsu()
        assert da.circle_size is None
        assert da.approach_rate is None

    def test_fields_set(self):
        ez = EasyOsu(retries=2.0)
        assert ez.retries == 2.0

        ac = AccuracyChallengeOsu(minimum_accuracy=95.0, restart=True)
        assert ac.minimum_accuracy == 95.0
        assert ac.restart is True

    def test_to_simple(self):
        ht = HalfTimeOsu(speed_change=0.75, adjust_pitch=True)
        simple = ht.to_simple()
        assert isinstance(simple, GameModSimple)
        assert str(simple.acronym) == "HT"
        assert "speed_change" in simple.settings
        assert simple.settings["speed_change"].as_float() == 0.75
        assert simple.settings["adjust_pitch"].as_bool() is True


# GameMod wrapper
class TestGameMod:
    def test_construct_from_inner(self):
        hd = GameMod(HiddenOsu())
        assert str(hd.acronym()) == "HD"
        assert hd.mode() == GameMode.Osu
        assert hd.kind() == GameModKind.DifficultyIncrease

    def test_new_factory(self):
        dt = GameMod.new("DT", GameMode.Taiko)
        assert isinstance(dt.inner, DoubleTimeTaiko)
        assert dt.mode() == GameMode.Taiko

    def test_new_unknown(self):
        gm = GameMod.new("XX", GameMode.Osu)
        assert gm.is_unknown()

    def test_class_level_factory(self):
        pf = GameMod.PerfectOsu(restart=True)
        assert isinstance(pf.inner, PerfectOsu)
        assert pf.inner.restart is True

    def test_intermode(self):
        hd = GameMod(HiddenOsu())
        im = hd.intermode()
        assert im == GameModIntermode.Hidden

    def test_equality(self):
        a = GameMod(HiddenOsu())
        b = GameMod(HiddenOsu())
        c = GameMod(HiddenMania())
        assert a == b
        assert a != c

    def test_to_dict_no_settings(self):
        d = GameMod(HiddenOsu()).to_dict()
        assert d == {"acronym": "HD"}

    def test_to_dict_with_settings(self):
        gm = GameMod(DifficultyAdjustOsu(circle_size=3.5))
        d = gm.to_dict()
        assert d["acronym"] == "DA"
        assert d["settings"]["circle_size"] == 3.5

    def test_from_dict_no_mode(self):
        gm = GameMod.from_dict({"acronym": "HD"})
        assert isinstance(gm.inner, HiddenOsu)

    def test_from_dict_with_mode(self):
        gm = GameMod.from_dict({"acronym": "HD"}, mode=GameMode.Mania)
        assert isinstance(gm.inner, HiddenMania)

    def test_from_dict_with_settings(self):
        gm = GameMod.from_dict(
            {"acronym": "DA", "settings": {"circle_size": 3.5}}, mode=GameMode.Osu
        )
        assert isinstance(gm.inner, DifficultyAdjustOsu)
        assert gm.inner.circle_size == 3.5

    def test_json_roundtrip(self):
        gm = GameMod(AccuracyChallengeOsu(minimum_accuracy=95.0, restart=True))
        j = gm.to_json()
        gm2 = GameMod.from_json(j, mode=GameMode.Osu)
        assert isinstance(gm2.inner, AccuracyChallengeOsu)
        assert gm2.inner.minimum_accuracy == 95.0
        assert gm2.inner.restart is True

    def test_str(self):
        assert str(GameMod(HiddenOsu())) == "HD"

    def test_unknown_variants(self):
        from osupp_mods.generated_mods import (
            UnknownCatch,
            UnknownMania,
            UnknownOsu,
            UnknownTaiko,
        )

        osu_unk = GameMod.new("XX", GameMode.Osu)
        assert isinstance(osu_unk.inner, UnknownOsu)
        tai_unk = GameMod.new("XX", GameMode.Taiko)
        assert isinstance(tai_unk.inner, UnknownTaiko)
        cat_unk = GameMod.new("XX", GameMode.Catch)
        assert isinstance(cat_unk.inner, UnknownCatch)
        man_unk = GameMod.new("XX", GameMode.Mania)
        assert isinstance(man_unk.inner, UnknownMania)

    def test_guess_mode_da_with_scroll_speed(self):
        gm = GameMod.from_dict(
            {"acronym": "DA", "settings": {"scroll_speed": 0.95}},
            deny_unknown_fields=True,
        )
        assert isinstance(gm.inner, DifficultyAdjustTaiko)
        assert gm.inner.scroll_speed == 0.95

    def test_bits(self):
        assert GameMod(HiddenOsu()).bits() == 8
        assert GameMod(DaycoreOsu()).bits() is None

    def test_all_141_via_new(self):
        from osupp_mods.game_mod import _ACR_MODE_MAP

        assert len(_ACR_MODE_MAP) == 140


# GameMods collection
class TestGameMods:
    def test_insert_and_iter(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(HardRockOsu()))
        assert len(mods) == 2

    def test_str_sorted(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(DoubleTimeOsu()))
        mods.insert(GameMod(TraceableOsu()))
        assert str(mods) == "DTHDTC"

    def test_order_matches_rust(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(HiddenMania()))
        mods.insert(GameMod(TraceableOsu()))
        mods.insert(GameMod(DoubleTimeOsu()))
        assert str(mods) == "DTHDTCHD"

    def test_contains(self):
        mods = GameMods()
        hd = GameMod(HiddenOsu())
        mods.insert(hd)
        assert mods.contains(hd)
        assert mods.contains_acronym("HD")
        assert not mods.contains_acronym("DT")

    def test_remove(self):
        mods = GameMods()
        hd = GameMod(HiddenOsu())
        mods.insert(hd)
        assert mods.remove(hd)
        assert len(mods) == 0

    def test_bits(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(HardRockOsu()))
        assert mods.bits() == 8 | 16

    def test_to_intermode(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(DoubleTimeOsu()))
        intermode = mods.to_intermode()
        assert intermode.contains(GameModIntermode.Hidden)
        assert intermode.contains(GameModIntermode.DoubleTime)

    def test_json_roundtrip(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        mods.insert(GameMod(AccuracyChallengeOsu(minimum_accuracy=90.0)))
        j = mods.to_json()
        mods2 = GameMods.from_json(j, mode=GameMode.Osu)
        assert mods2.contains_acronym("HD")
        assert mods2.contains_acronym("AC")

    def test_empty_str(self):
        mods = GameMods()
        assert str(mods) == "NM"

    def test_from_iter(self):
        mods = GameMods.from_iter([GameMod(HiddenOsu()), GameMod(HardRockOsu())])
        assert len(mods) == 2

    def test_get(self):
        mods = GameMods()
        mods.insert(GameMod(HiddenOsu()))
        gm = mods.get("HD")
        assert gm is not None
        assert isinstance(gm.inner, HiddenOsu)


# GameModIntermode
class TestGameModIntermode:
    def test_all_variants_count(self):
        variants = [v for v in GameModIntermode if v != GameModIntermode.Unknown]
        assert len(variants) == 69

    def test_acronym(self):
        assert str(GameModIntermode.Hidden.acronym()) == "HD"
        assert str(GameModIntermode.DoubleTime.acronym()) == "DT"
        assert str(GameModIntermode.TenKeys.acronym()) == "10K"
        assert str(GameModIntermode.ScoreV2.acronym()) == "SV2"

    def test_bits(self):
        assert GameModIntermode.Hidden.bits() == 8
        assert GameModIntermode.DoubleTime.bits() == 64
        assert GameModIntermode.Daycore.bits() is None

    def test_kind(self):
        assert GameModIntermode.Easy.kind() == GameModKind.DifficultyReduction
        assert GameModIntermode.HardRock.kind() == GameModKind.DifficultyIncrease
        assert GameModIntermode.Autoplay.kind() == GameModKind.Automation

    def test_from_acronym(self):
        assert GameModIntermode.from_acronym("HD") == GameModIntermode.Hidden
        assert GameModIntermode.from_acronym("10K") == GameModIntermode.TenKeys
        assert GameModIntermode.from_acronym("SV2") == GameModIntermode.ScoreV2
        assert GameModIntermode.from_acronym("XX") == GameModIntermode.Unknown

    def test_try_from_bits(self):
        assert GameModIntermode.try_from_bits(8) == GameModIntermode.Hidden
        assert GameModIntermode.try_from_bits(64) == GameModIntermode.DoubleTime
        assert GameModIntermode.try_from_bits(99999) is None

    def test_ordering(self):
        mods = sorted(
            [
                GameModIntermode.Wiggle,
                GameModIntermode.DoubleTime,
                GameModIntermode.Hidden,
            ]
        )
        assert mods[0] == GameModIntermode.DoubleTime
        assert mods[1] == GameModIntermode.Hidden
        assert mods[2] == GameModIntermode.Wiggle

    def test_str(self):
        assert str(GameModIntermode.Hidden) == "HD"


# GameModsIntermode
class TestGameModsIntermode:
    def test_insert_and_contains(self):
        mods = GameModsIntermode()
        mods.insert(GameModIntermode.Hidden)
        assert mods.contains(GameModIntermode.Hidden)
        assert not mods.contains(GameModIntermode.HardRock)

    def test_sorted_str(self):
        mods = GameModsIntermode(
            [
                GameModIntermode.Wiggle,
                GameModIntermode.FadeIn,
                GameModIntermode.Easy,
                GameModIntermode.HardRock,
            ]
        )
        assert str(mods) == "EZFIHRWG"

    def test_len(self):
        mods = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.DoubleTime])
        assert len(mods) == 2

    def test_remove(self):
        mods = GameModsIntermode([GameModIntermode.Hidden])
        assert mods.remove(GameModIntermode.Hidden)
        assert mods.is_empty()

    def test_bits_accumulated(self):
        mods = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.HardRock])
        assert mods.bits() == 8 | 16

    def test_checked_bits_none(self):
        mods = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.Daycore])
        assert mods.checked_bits() is None

    def test_from_bits(self):
        mods = GameModsIntermode.from_bits(8 | 16)
        assert mods.contains(GameModIntermode.Hidden)
        assert mods.contains(GameModIntermode.HardRock)

    def test_from_acronyms(self):
        mods = GameModsIntermode.from_acronyms(["HD", "DT", "HR"])
        assert len(mods) == 3

    def test_parse(self):
        mods = GameModsIntermode.parse("HDHRDT")
        assert mods.contains(GameModIntermode.Hidden)
        assert mods.contains(GameModIntermode.HardRock)
        assert mods.contains(GameModIntermode.DoubleTime)

    def test_parse_long_acronyms(self):
        mods = GameModsIntermode.parse("10KSV2")
        assert mods.contains(GameModIntermode.TenKeys)
        assert mods.contains(GameModIntermode.ScoreV2)

    def test_union(self):
        a = GameModsIntermode([GameModIntermode.Hidden])
        b = GameModsIntermode([GameModIntermode.HardRock])
        c = a | b
        assert c.contains(GameModIntermode.Hidden)
        assert c.contains(GameModIntermode.HardRock)

    def test_difference(self):
        a = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.HardRock])
        b = GameModsIntermode([GameModIntermode.HardRock])
        c = a - b
        assert c.contains(GameModIntermode.Hidden)
        assert not c.contains(GameModIntermode.HardRock)

    def test_intersection(self):
        a = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.HardRock])
        b = GameModsIntermode([GameModIntermode.HardRock, GameModIntermode.DoubleTime])
        c = a.intersection(b)
        assert c.contains(GameModIntermode.HardRock)
        assert not c.contains(GameModIntermode.Hidden)

    def test_with_mode(self):
        intermode = GameModsIntermode(
            [GameModIntermode.Hidden, GameModIntermode.HardRock]
        )
        mods = intermode.with_mode(GameMode.Osu)
        assert mods.contains_acronym("HD")
        assert mods.contains_acronym("HR")

    def test_try_with_mode_success(self):
        intermode = GameModsIntermode([GameModIntermode.Hidden])
        mods = intermode.try_with_mode(GameMode.Osu)
        assert mods is not None
        assert mods.contains_acronym("HD")

    def test_try_with_mode_fail(self):
        intermode = GameModsIntermode([GameModIntermode.FloatingFruits])
        mods = intermode.try_with_mode(GameMode.Osu)
        assert mods is None

    def test_empty_str(self):
        assert str(GameModsIntermode()) == "NM"

    def test_hash(self):
        a = GameModsIntermode([GameModIntermode.Hidden])
        b = GameModsIntermode([GameModIntermode.Hidden])
        assert hash(a) == hash(b)

    def test_json_roundtrip(self):
        mods = GameModsIntermode([GameModIntermode.Hidden, GameModIntermode.DoubleTime])
        j = mods.to_json()
        import json

        raw = json.loads(j)
        mods2 = GameModsIntermode.parse(raw)
        assert mods == mods2


# GameModsLegacy
class TestGameModsLegacy:
    def test_named_constants(self):
        assert int(GameModsLegacy.NoMod) == 0
        assert int(GameModsLegacy.Hidden) == 8
        assert int(GameModsLegacy.HardRock) == 16
        assert int(GameModsLegacy.DoubleTime) == 64
        assert int(GameModsLegacy.Nightcore) == 576
        assert int(GameModsLegacy.Perfect) == 16416
        assert int(GameModsLegacy.ScoreV2) == 536870912
        assert int(GameModsLegacy.Mirror) == 1073741824

    def test_bitwise_or(self):
        hdhr = GameModsLegacy.Hidden | GameModsLegacy.HardRock
        assert int(hdhr) == 8 | 16

    def test_contains(self):
        nc = GameModsLegacy.Nightcore
        assert nc.contains(GameModsLegacy.DoubleTime)
        assert nc.contains(GameModsLegacy.Nightcore)

    def test_str(self):
        assert str(GameModsLegacy.NoMod) == "NM"
        hdhr = GameModsLegacy.Hidden | GameModsLegacy.HardRock
        assert "HD" in str(hdhr)
        assert "HR" in str(hdhr)

    def test_parse(self):
        mods = GameModsLegacy.parse("HDHRDT")
        assert mods.contains(GameModsLegacy.Hidden)
        assert mods.contains(GameModsLegacy.HardRock)
        assert mods.contains(GameModsLegacy.DoubleTime)

    def test_parse_case_insensitive(self):
        mods = GameModsLegacy.parse("hdhr")
        assert mods.contains(GameModsLegacy.Hidden)
        assert mods.contains(GameModsLegacy.HardRock)

    def test_from_bits(self):
        mods = GameModsLegacy.from_bits(8 | 16)
        assert mods == GameModsLegacy.Hidden | GameModsLegacy.HardRock

    def test_clock_rate(self):
        assert (GameModsLegacy.DoubleTime).clock_rate() == 1.5
        assert (GameModsLegacy.Nightcore).clock_rate() == 1.5
        assert (GameModsLegacy.HalfTime).clock_rate() == 0.75
        assert (GameModsLegacy.Hidden).clock_rate() == 1.0

    def test_iter(self):
        hdnc = GameModsLegacy.Hidden | GameModsLegacy.Nightcore
        items = list(hdnc.iter())
        names = hdnc.named_mods()
        assert "Hidden" in names
        assert "Nightcore" in names
        assert "DoubleTime" not in names

    def test_acronyms(self):
        mods = GameModsLegacy.Hidden | GameModsLegacy.HardRock
        acrs = mods.acronyms()
        assert "HD" in acrs
        assert "HR" in acrs

    def test_nomod_iter(self):
        items = list(GameModsLegacy.NoMod.iter())
        assert len(items) == 1
        assert items[0] == GameModsLegacy.NoMod

    def test_equality(self):
        assert GameModsLegacy.Hidden == GameModsLegacy.Hidden
        assert GameModsLegacy.Hidden != GameModsLegacy.HardRock
        assert GameModsLegacy.Hidden == 8

    def test_subtract(self):
        mods = GameModsLegacy.Hidden | GameModsLegacy.HardRock
        result = mods - GameModsLegacy.Hidden
        assert not result.contains(GameModsLegacy.Hidden)
        assert result.contains(GameModsLegacy.HardRock)

    def test_xor(self):
        a = GameModsLegacy.Hidden | GameModsLegacy.HardRock
        b = GameModsLegacy.HardRock
        c = a ^ b
        assert c.contains(GameModsLegacy.Hidden)
        assert not c.contains(GameModsLegacy.HardRock)

    def test_all_32_named_bits(self):
        from osupp_mods.game_mods_legacy import _NAMED_BITS

        assert len(_NAMED_BITS) == 32

    def test_mania_keys(self):
        assert int(GameModsLegacy.Key4) == 32768
        assert int(GameModsLegacy.Key9) == 16777216
        assert int(GameModsLegacy.Key1) == 67108864


# GameModSimple / SettingSimple
class TestSettingSimple:
    def test_bool(self):
        s = SettingSimple(True)
        assert s.is_bool()
        assert s.as_bool() is True
        with pytest.raises(TypeError):
            s.as_float()

    def test_float(self):
        s = SettingSimple(3.14)
        assert s.is_float()
        assert s.as_float() == 3.14

    def test_str(self):
        s = SettingSimple("combo")
        assert s.is_str()
        assert s.as_str() == "combo"

    def test_equality(self):
        assert SettingSimple(True) == SettingSimple(True)
        assert SettingSimple(3.0) == 3.0


class TestGameModSimple:
    def test_from_mod(self):
        gm = GameMod(AccuracyChallengeOsu(minimum_accuracy=90.5, restart=False))
        simple = gm.into_simple()
        assert str(simple.acronym) == "AC"
        assert "minimum_accuracy" in simple.settings
        assert simple.settings["minimum_accuracy"].as_float() == 90.5
        assert "restart" in simple.settings
        assert simple.settings["restart"].as_bool() is False

    def test_no_settings(self):
        gm = GameMod(HiddenOsu())
        simple = gm.into_simple()
        assert str(simple.acronym) == "HD"
        assert simple.settings == {}


# Cross-type integration
class TestIntegration:
    def test_bits_roundtrip_legacy_to_intermode(self):
        legacy = (
            GameModsLegacy.Hidden | GameModsLegacy.HardRock | GameModsLegacy.DoubleTime
        )
        intermode = GameModsIntermode.from_bits(legacy.bits())
        assert intermode.contains(GameModIntermode.Hidden)
        assert intermode.contains(GameModIntermode.HardRock)
        assert intermode.contains(GameModIntermode.DoubleTime)

    def test_intermode_to_gamemods_and_back(self):
        intermode = GameModsIntermode(
            [
                GameModIntermode.Hidden,
                GameModIntermode.DoubleTime,
            ]
        )
        mods = intermode.with_mode(GameMode.Taiko)
        assert mods.contains_acronym("HD")
        assert mods.contains_acronym("DT")
        hd = mods.get("HD")
        assert isinstance(hd.inner, HiddenTaiko)

    def test_gamemod_to_intermode(self):
        gm = GameMod(NightcoreMania())
        im = gm.intermode()
        assert im == GameModIntermode.Nightcore

    def test_all_intermode_variants_have_acronym(self):
        for variant in GameModIntermode:
            if variant == GameModIntermode.Unknown:
                continue
            acr = variant.acronym()
            assert isinstance(acr, Acronym)
            assert len(str(acr)) >= 1

    def test_gamemod_new_all_known(self):
        from osupp_mods.game_mod import _ACR_MODE_MAP

        for (acr, mode), inner_cls in _ACR_MODE_MAP.items():
            gm = GameMod.new(acr, mode)
            assert not gm.is_unknown(), f"{acr} on {mode} should not be unknown"
            assert str(gm.acronym()) == acr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
