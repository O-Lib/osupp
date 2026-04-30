from __future__ import annotations

import bisect
import io
import math

from section.enums import GameMode, HitSoundType, SampleBank
from section.hit_objects.hit_objects import (
    HitObjectCircle,
    HitObjectHold,
    HitObjectSlider,
    HitObjectSpinner,
    HitObjectType,
    HitSampleDefaultName,
)
from section.hit_objects.slider import (
    SliderEventType,
    generate_slider_events,
)
from section.timing_points import (
    ControlPoints,
    DifficultyPoint,
    SamplePoint,
    TimingPoint,
)

_BASE_SCORING_DIST = 100.0

_bisect_right = bisect.bisect_right


def encode_beatmap(beatmap, writer: io.TextIOBase, *, lazer_compatible: bool = False) -> None:
    writer.write(f"osu file format v{beatmap.format_version}\n\n")

    _encode_general(beatmap, writer)
    writer.write("\n")

    _encode_editor(beatmap, writer)
    writer.write("\n")

    _encode_metadata(beatmap, writer)
    writer.write("\n")

    _encode_difficulty(beatmap, writer)
    writer.write("\n")

    _encode_events(beatmap, writer)
    writer.write("\n")

    _encode_timing_points(beatmap, writer, lazer_compatible=lazer_compatible)
    writer.write("\n")

    _encode_colors(beatmap, writer)
    writer.write("\n")

    _encode_hit_objects(beatmap, writer)


def _encode_general(beatmap, writer) -> None:
    writer.write("[General]\n")
    writer.write(f"AudioFilename: {beatmap.general.audio_filename}\n")
    writer.write(f"AudioLeadIn: {beatmap.general.audio_lead_in}\n")
    writer.write(f"PreviewTime: {beatmap.general.preview_time}\n")
    writer.write(f"Countdown: {beatmap.general.countdown.value}\n")

    sample_bank = getattr(
        beatmap.general,
        "default_sample_bank",
        getattr(beatmap.general, "sample_bank", None),
    )

    if sample_bank is not None:
        sample_set = sample_bank if hasattr(sample_bank, "value") else int(sample_bank)
    else:
        sample_set = 1

    writer.write(f"SampleSet: {sample_set}\n")
    writer.write(f"StackLeniency: {beatmap.general.stack_leniency}\n")
    writer.write(f"Mode: {beatmap.general.mode.value}\n")
    writer.write(
        f"LetterboxInBreaks: {1 if beatmap.general.letterbox_in_breaks else 0}\n"
    )

    if beatmap.general.epilepsy_warning:
        writer.write("EpilepsyWarning: 1\n")
    if getattr(beatmap.general, "countdown_offset", 0) > 0:
        writer.write(f"CountdownOffset: {beatmap.general.countdown_offset}\n")
    if beatmap.general.mode == GameMode.Mania:
        writer.write(f"SpecialStyle: {1 if beatmap.general.special_style else 0}\n")

    writer.write(
        f"WidescreenStoryboard: {1 if beatmap.general.widescreen_storyboard else 0}\n"
    )

    if beatmap.general.samples_match_playback_rate:
        writer.write("SamplesMatchPlaybackRate: 1\n")


def _encode_editor(beatmap, writer) -> None:
    writer.write("[Editor]\n")
    if beatmap.editor.bookmarks:
        bookmarks_str = ",".join(str(b) for b in beatmap.editor.bookmarks)
        writer.write(f"Bookmarks: {bookmarks_str}\n")

    writer.write(f"DistanceSpacing: {beatmap.editor.distance_spacing}\n")
    writer.write(f"BeatDivisor: {beatmap.editor.beat_divisor}\n")
    writer.write(f"GridSize: {beatmap.editor.grid_size}\n")
    writer.write(f"TimelineZoom: {beatmap.editor.timeline_zoom}\n")


def _encode_metadata(beatmap, writer) -> None:
    writer.write("[Metadata]\n")
    writer.write(f"Title:{beatmap.metadata.title}\n")
    if beatmap.metadata.title_unicode:
        writer.write(f"TitleUnicode:{beatmap.metadata.title_unicode}\n")

    writer.write(f"Artist:{beatmap.metadata.artist}\n")
    if beatmap.metadata.artist_unicode:
        writer.write(f"ArtistUnicode:{beatmap.metadata.artist_unicode}\n")

    writer.write(f"Creator:{beatmap.metadata.creator}\n")
    writer.write(f"Version:{beatmap.metadata.version}\n")

    if beatmap.metadata.source:
        writer.write(f"Source:{beatmap.metadata.source}\n")
    if beatmap.metadata.tags:
        writer.write(f"Tags:{beatmap.metadata.tags}\n")

    writer.write(f"BeatmapID:{beatmap.metadata.beatmap_id}\n")
    writer.write(f"BeatmapSetID:{beatmap.metadata.beatmap_set_id}\n")


def _encode_difficulty(beatmap, writer) -> None:
    writer.write("[Difficulty]\n")
    writer.write(f"HPDrainRate:{beatmap.difficulty.hp_drain_rate}\n")
    writer.write(f"CircleSize:{beatmap.difficulty.circle_size}\n")
    writer.write(f"OverallDifficulty:{beatmap.difficulty.overall_difficulty}\n")
    writer.write(f"ApproachRate:{beatmap.difficulty.approach_rate}\n")
    writer.write(f"SliderMultiplier:{beatmap.difficulty.slider_multiplier}\n")
    writer.write(f"SliderTickRate:{beatmap.difficulty.slider_tick_rate}\n")


def _encode_events(beatmap, writer) -> None:
    writer.write("[Events]\n")
    if beatmap.events.background_file:
        writer.write(f'0,0,"{beatmap.events.background_file}",0,0\n')

    for b in beatmap.events.breaks:
        writer.write(f"2,{b.start_time},{b.end_time}\n")


def _encode_colors(beatmap, writer) -> None:
    writer.write("[Colours]\n")
    for i, color in enumerate(beatmap.colors.custom_combo_colors, start=1):
        writer.write(f"Combo{i} : {color.red},{color.green},{color.blue}\n")

    for custom in beatmap.colors.custom_colors:
        writer.write(
            f"{custom.name} : {custom.color.red},{custom.color.green},{custom.color.blue}\n"
        )


def _precision_adjusted_beat_len(
    slider_velocity: float, beat_len: float, mode: GameMode
) -> float:
    sv_as_beat_len = -100.0 / slider_velocity
    if sv_as_beat_len < 0.0:
        if mode in (GameMode.Osu, GameMode.Catch):
            bpm_multiplier = max(10.0, min(10_000.0, -sv_as_beat_len)) / 100.0
        else:  # Taiko, Mania
            bpm_multiplier = max(10.0, min(1000.0, -sv_as_beat_len)) / 100.0
    else:
        bpm_multiplier = 1.0
    return beat_len * bpm_multiplier


def _saturating_difficulty_at(cp: ControlPoints, time: float) -> DifficultyPoint | None:
    if not cp.difficulty_points:
        return None
    lo, hi = 0, len(cp.difficulty_points)
    while lo < hi:
        mid = (lo + hi) // 2
        if cp.difficulty_points[mid].time <= time:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return None
    return cp.difficulty_points[lo - 1]


def _saturating_timing_at(cp: ControlPoints, time: float) -> TimingPoint | None:
    if not cp.timing_points:
        return None
    lo, hi = 0, len(cp.timing_points)
    while lo < hi:
        mid = (lo + hi) // 2
        if cp.timing_points[mid].time <= time:
            lo = mid + 1
        else:
            hi = mid
    return cp.timing_points[max(0, lo - 1)]


def _slider_velocity_for(
    slider: HitObjectSlider,
    start_time: float,
    cp: ControlPoints,
    slider_multiplier: float,
    mode: GameMode,
) -> float:
    tp = _saturating_timing_at(cp, start_time)
    beat_len = tp.beat_len if tp is not None else 60_000.0 / 60.0

    dp = _saturating_difficulty_at(cp, start_time)
    sv = dp.slider_velocity if dp is not None else 1.0

    adjusted = _precision_adjusted_beat_len(sv, beat_len, mode)
    if adjusted == 0.0:
        return 0.0
    return _BASE_SCORING_DIST * slider_multiplier / adjusted


def _collect_sample_from_hit_samples(
    samples: list, time: float, *, lazer_compatible: bool = False
) -> SamplePoint | None:
    if not samples:
        return None
    volume = max(s.volume for s in samples)
    custom = max(s.custom_sample_bank for s in samples)

    if lazer_compatible:
        bank: SampleBank | None = None
        for s in samples:
            if s.name_default == HitSampleDefaultName.Normal:
                bank = s.bank
                break
        if bank is None:
            bank = samples[0].bank
    else:
        bank = SampleBank.Normal

    return SamplePoint(
        time=time,
        sample_bank=bank,
        sample_volume=volume,
        custom_sample_bank=custom,
    )


def _collect_samples(beatmap, cp: ControlPoints, *, lazer_compatible: bool = False) -> None:
    mode = beatmap.general.mode
    slider_multiplier = beatmap.difficulty.slider_multiplier

    collected: list[SamplePoint] = []

    for h in beatmap.hit_objects.hit_objects:
        kind = h.kind

        if isinstance(kind, HitObjectCircle):
            end_time = h.start_time
        elif isinstance(kind, HitObjectSpinner):
            end_time = h.start_time + kind.duration
        elif isinstance(kind, HitObjectHold):
            end_time = h.start_time + kind.duration
        elif isinstance(kind, HitObjectSlider):
            curve_dist = kind.path.curve().dist()
            velocity = _slider_velocity_for(
                kind, h.start_time, beatmap.control_points, slider_multiplier, mode
            )
            span_count = kind.repeat_count + 1
            if velocity > 0.0:
                duration = span_count * curve_dist / velocity
            else:
                duration = 0.0
            end_time = h.start_time + duration
        else:
            end_time = h.start_time

        sp = _collect_sample_from_hit_samples(h.samples, end_time, lazer_compatible=lazer_compatible)
        if sp is not None:
            collected.append(sp)

        if isinstance(kind, HitObjectSlider):
            if mode == GameMode.Osu:
                tick_dist_factor = velocity * 60_000.0
                tp = _saturating_timing_at(beatmap.control_points, h.start_time)
                beat_len = tp.beat_len if tp is not None else 1000.0
                dp = _saturating_difficulty_at(beatmap.control_points, h.start_time)
                sv = dp.slider_velocity if dp is not None else 1.0
                gen_ticks = dp.generate_ticks if dp is not None else True
                tick_dist_multiplier = (1.0 / sv) if beatmap.format_version < 8 else 1.0
                scoring_dist = velocity * beat_len
                if gen_ticks:
                    tick_dist = scoring_dist / beatmap.difficulty.slider_tick_rate * tick_dist_multiplier
                else:
                    tick_dist = math.inf

                span_duration = (curve_dist / velocity) if velocity > 0.0 else 0.0

                if span_duration <= 0.0 or curve_dist <= 0.0:
                    continue

                events = list(
                    generate_slider_events(
                        h.start_time,
                        span_duration,
                        velocity,
                        tick_dist,
                        curve_dist,
                        span_count,
                    )
                )

                for ev in events:
                    if ev.kind == SliderEventType.Head:
                        node_samples = (
                            kind.node_samples[0] if kind.node_samples else h.samples
                        )
                        sp = _collect_sample_from_hit_samples(node_samples, ev.time, lazer_compatible=lazer_compatible)
                        if sp is not None:
                            collected.append(sp)
                    elif ev.kind == SliderEventType.Repeat:
                        idx = ev.span_idx + 1
                        node_samples = (
                            kind.node_samples[idx]
                            if idx < len(kind.node_samples)
                            else h.samples
                        )
                        sp = _collect_sample_from_hit_samples(node_samples, ev.time, lazer_compatible=lazer_compatible)
                        if sp is not None:
                            collected.append(sp)
                    elif ev.kind == SliderEventType.Tail:
                        idx = kind.repeat_count + 1
                        node_samples = (
                            kind.node_samples[idx]
                            if idx < len(kind.node_samples)
                            else h.samples
                        )
                        sp = _collect_sample_from_hit_samples(node_samples, ev.time, lazer_compatible=lazer_compatible)
                        if sp is not None:
                            collected.append(sp)
            elif mode == GameMode.Catch:
                dp = _saturating_difficulty_at(beatmap.control_points, h.start_time)
                sv = dp.slider_velocity if dp is not None else 1.0
                tick_dist_multiplier = (1.0 / sv) if beatmap.format_version < 8 else 1.0
                tick_dist = (
                    _BASE_SCORING_DIST
                    * slider_multiplier
                    / beatmap.difficulty.slider_tick_rate
                    * tick_dist_multiplier
                )

                span_duration = (curve_dist / velocity) if velocity > 0.0 else 0.0

                if span_duration <= 0.0 or curve_dist <= 0.0:
                    continue

                events = list(
                    generate_slider_events(
                        h.start_time,
                        span_duration,
                        velocity,
                        tick_dist,
                        curve_dist,
                        span_count,
                    )
                )

                node_idx = 0
                for ev in events:
                    if ev.kind in (
                        SliderEventType.Head,
                        SliderEventType.Repeat,
                        SliderEventType.Tail,
                    ):
                        node_samples = (
                            kind.node_samples[node_idx]
                            if node_idx < len(kind.node_samples)
                            else h.samples
                        )
                        sp = _collect_sample_from_hit_samples(node_samples, ev.time, lazer_compatible=lazer_compatible)
                        if sp is not None:
                            collected.append(sp)
                        node_idx += 1
            elif mode == GameMode.Mania:
                sp = _collect_sample_from_hit_samples(h.samples, h.start_time, lazer_compatible=lazer_compatible)
                if sp is not None:
                    collected.append(sp)

    collected.sort(key=lambda s: s.time)
    if not collected:
        return

    iterator = iter(collected)
    first = next(iterator)
    cp.add_sample(first)
    last = first
    for s in iterator:
        if not s.is_redundant(last):
            cp.add_sample(s)
            last = s


def _clone_control_points(cp: ControlPoints) -> ControlPoints:
    new = ControlPoints()
    new.timing_points = list(cp.timing_points)
    new.difficulty_points = list(cp.difficulty_points)
    new.effect_points = list(cp.effect_points)
    new.sample_points = list(cp.sample_points)
    return new


def _encode_timing_points(beatmap, writer, *, lazer_compatible: bool = False) -> None:
    if lazer_compatible:
        cp = _clone_control_points(beatmap.timing_points.control_points)
        _collect_samples(beatmap, cp, lazer_compatible=True)
    else:
        cp = beatmap.timing_points.control_points

    writer.write("[TimingPoints]\n")

    timing_by_time = {tp.time: tp for tp in cp.timing_points}
    diff_by_time = {dp.time: dp for dp in cp.difficulty_points}
    eff_by_time = {ep.time: ep for ep in cp.effect_points}
    sample_by_time = {sp.time: sp for sp in cp.sample_points}

    all_times = sorted(
        set(timing_by_time)
        | set(diff_by_time)
        | set(eff_by_time)
        | set(sample_by_time)
    )

    active_meter = 4
    active_sv = 1.0
    active_generate_ticks = True
    active_kiai = False
    active_bank = 1
    active_volume = 100
    active_custom_bank = 0

    for time in all_times:
        tp = timing_by_time.get(time)
        dp = diff_by_time.get(time)
        ep = eff_by_time.get(time)
        sp = sample_by_time.get(time)

        if dp is not None:
            active_sv = dp.slider_velocity
            active_generate_ticks = dp.generate_ticks
        if ep is not None:
            active_kiai = ep.kiai
        if sp is not None:
            active_bank = sp.sample_bank.value
            active_volume = sp.sample_volume
            active_custom_bank = sp.custom_sample_bank

        if tp is not None:
            active_meter = tp.time_signature
            omit_bar = tp.omit_first_bar_line
            effect_flags = (1 if active_kiai else 0) | (8 if omit_bar else 0)
            writer.write(
                f"{time},{tp.beat_len},{active_meter},"
                f"{active_bank},{active_custom_bank},{active_volume},"
                f"1,{effect_flags}\n"
            )

            if abs(active_sv - 1.0) <= 1e-9 and active_generate_ticks:
                continue

        if not active_generate_ticks:
            beat_len_str = "NaN"
        else:
            beat_len = -100.0 / active_sv if active_sv != 0 else -100.0
            beat_len_str = f"{beat_len}"
        effect_flags = 1 if active_kiai else 0
        writer.write(
            f"{time},{beat_len_str},{active_meter},"
            f"{active_bank},{active_custom_bank},{active_volume},"
            f"0,{effect_flags}\n"
        )


def _encode_hit_objects(beatmap, writer) -> None:
    writer.write("[HitObjects]\n")

    for obj in beatmap.hit_objects.hit_objects:
        x, y = 0.0, 0.0
        type_flag = 0

        if isinstance(obj.kind, HitObjectCircle):
            x, y = obj.kind.pos.x, obj.kind.pos.y
            type_flag = HitObjectType.CIRCLE
            if obj.kind.new_combo:
                type_flag |= HitObjectType.NEW_COMBO
            type_flag |= obj.kind.combo_offset << 4

        elif isinstance(obj.kind, HitObjectSlider):
            x, y = obj.kind.pos.x, obj.kind.pos.y
            type_flag = HitObjectType.SLIDER
            if obj.kind.new_combo:
                type_flag |= HitObjectType.NEW_COMBO
            type_flag |= obj.kind.combo_offset << 4

        elif isinstance(obj.kind, HitObjectSpinner):
            x, y = 256.0, 192.0
            type_flag = HitObjectType.SPINNER
            if obj.kind.new_combo:
                type_flag |= HitObjectType.NEW_COMBO

        elif isinstance(obj.kind, HitObjectHold):
            x, y = obj.kind.pos_x, 192.0
            type_flag = HitObjectType.HOLD

        sound_flag = 0
        for sample in obj.samples:
            if sample.name_default:
                if sample.name_default.value == "hitwhistle":
                    sound_flag |= HitSoundType.WHISTLE
                elif sample.name_default.value == "hitfinish":
                    sound_flag |= HitSoundType.FINISH
                elif sample.name_default.value == "hitclap":
                    sound_flag |= HitSoundType.CLAP
                elif sample.name_default.value == "hitnormal":
                    sound_flag |= HitSoundType.NORMAL

        def fmt(n):
            return f"{int(n)}" if n == int(n) else f"{n}"

        writer.write(
            f"{fmt(x)},{fmt(y)},{fmt(obj.start_time)},{type_flag},{sound_flag},"
        )

        if isinstance(obj.kind, HitObjectCircle):
            _write_sample_bank(writer, obj.samples, False, beatmap.general.mode)

        elif isinstance(obj.kind, HitObjectSpinner):
            writer.write(f"{fmt(obj.start_time + obj.kind.duration)},")
            _write_sample_bank(writer, obj.samples, False, beatmap.general.mode)

        elif isinstance(obj.kind, HitObjectHold):
            writer.write(f"{fmt(obj.start_time + obj.kind.duration)}:")
            _write_sample_bank(writer, obj.samples, False, beatmap.general.mode)

        elif isinstance(obj.kind, HitObjectSlider):
            _write_slider_path(writer, obj.kind)
            _write_sample_bank(writer, obj.samples, False, beatmap.general.mode)

        writer.write("\n")


def _write_slider_path(writer, slider) -> None:
    points = slider.path.control_points
    if not points:
        writer.write("L|0:0,1,0,0|0,0:0|0:0,")
        return

    last_type = None
    for i, p in enumerate(points):
        path_type = p.path_type
        if path_type:
            needs_explicit = (path_type != last_type) or (
                path_type.kind.name == "PerfectCurve"
            )

            if i > 1:
                p1 = slider.pos + points[i - 1].pos
                p2 = slider.pos + points[i - 2].pos
                if int(p1.x) == int(p2.x) and int(p1.y) == int(p2.y):
                    needs_explicit = True

            if needs_explicit:
                if path_type.kind.name == "BSpline":
                    writer.write("B")
                elif path_type.kind.name == "Catmull":
                    writer.write("C")
                elif path_type.kind.name == "PerfectCurve":
                    writer.write("P")
                elif path_type.kind.name == "Linear":
                    writer.write("L")

                writer.write("," if i == len(points) - 1 else "|")
                last_type = path_type
            else:
                writer.write(
                    f"{int(slider.pos.x + p.pos.x)}:{int(slider.pos.y + p.pos.y)}|"
                )

        if i != 0:
            writer.write(f"{int(slider.pos.x + p.pos.x)}:{int(slider.pos.y + p.pos.y)}")
            writer.write("," if i == len(points) - 1 else "|")

    dist = slider.path.expected_dist if slider.path.expected_dist is not None else 0
    writer.write(f"{slider.repeat_count + 1},{dist},")

    nodes = slider.repeat_count + 2
    writer.write("0|" * (nodes - 1) + "0,")
    writer.write("0:0|" * (nodes - 1) + "0:0,")


def _write_sample_bank(writer, samples, banks_only: bool, mode: GameMode) -> None:
    normal_bank = 0
    add_bank = 0
    volume = 0
    custom_bank = 0
    filename = ""

    if samples:
        s = samples[0]
        normal_bank = s.bank.value if hasattr(s.bank, "value") else 0
        add_bank = s.bank.value if hasattr(s.bank, "value") else 0
        volume = s.volume
        custom_bank = s.custom_sample_bank
        if s.name_file:
            filename = s.name_file

    if mode != GameMode.Osu:
        custom_bank = 0
        volume = 0

    writer.write(f"{normal_bank}:{add_bank}")
    if banks_only:
        return

    writer.write(f":{custom_bank}:{volume}:")
    if filename:
        writer.write(f"{filename}")
