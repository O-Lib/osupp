from __future__ import annotations

import io

from section.enums import GameMode, HitSoundType
from section.hit_objects.hit_objects import (
    HitObjectCircle,
    HitObjectHold,
    HitObjectSlider,
    HitObjectSpinner,
    HitObjectType,
)


def encode_beatmap(beatmap, writer: io.TextIOBase) -> None:
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

    _encode_timing_points(beatmap, writer)
    writer.write("\n")

    _encode_colors(beatmap, writer)
    writer.write("\n")

    _encode_hit_objects(beatmap, writer)


def _encode_general(beatmap, writer) -> None:
    #
    writer.write("[General]\n")
    writer.write(f"AudioFilename: {beatmap.general.audio_filename}\n")
    writer.write(f"AudioLeadIn: {beatmap.general.audio_lead_in}\n")
    writer.write(f"PreviewTime: {beatmap.general.preview_time}\n")
    writer.write(f"Countdown: {beatmap.general.countdown.value}\n")

    sample_set = (
        beatmap.general.sample_bank.value
        if hasattr(beatmap.general, "sample_bank")
        else 1
    )
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
    #
    writer.write("[Editor]\n")
    if beatmap.editor.bookmarks:
        bookmarks_str = ",".join(str(b) for b in beatmap.editor.bookmarks)
        writer.write(f"Bookmarks: {bookmarks_str}\n")

    writer.write(f"DistanceSpacing: {beatmap.editor.distance_spacing}\n")
    writer.write(f"BeatDivisor: {beatmap.editor.beat_divisor}\n")
    writer.write(f"GridSize: {beatmap.editor.grid_size}\n")
    writer.write(f"TimelineZoom: {beatmap.editor.timeline_zoom}\n")


def _encode_metadata(beatmap, writer) -> None:
    #
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
    #
    writer.write("[Difficulty]\n")
    writer.write(f"HPDrainRate:{beatmap.difficulty.hp_drain_rate}\n")
    writer.write(f"CircleSize:{beatmap.difficulty.circle_size}\n")
    writer.write(f"OverallDifficulty:{beatmap.difficulty.overall_difficulty}\n")
    writer.write(f"ApproachRate:{beatmap.difficulty.approach_rate}\n")
    writer.write(f"SliderMultiplier:{beatmap.difficulty.slider_multiplier}\n")
    writer.write(f"SliderTickRate:{beatmap.difficulty.slider_tick_rate}\n")


def _encode_events(beatmap, writer) -> None:
    #
    writer.write("[Events]\n")
    if beatmap.events.background_file:
        writer.write(f'0,0,"{beatmap.events.background_file}",0,0\n')

    for b in beatmap.events.breaks:
        writer.write(f"2,{b.start_time},{b.end_time}\n")


def _encode_colors(beatmap, writer) -> None:
    #
    writer.write("[Colours]\n")
    for i, color in enumerate(beatmap.colors.custom_combo_colors, start=1):
        writer.write(f"Combo{i} : {color.red},{color.green},{color.blue}\n")

    for custom in beatmap.colors.custom_colors:
        writer.write(
            f"{custom.name} : {custom.color.red},{custom.color.green},{custom.color.blue}\n"
        )


def _encode_timing_points(beatmap, writer) -> None:
    timing_points_state = beatmap.timing_points

    writer.write("[TimingPoints]\n")

    all_times = set()
    tps = getattr(
        timing_points_state, "timing_points", getattr(timing_points_state, "points", [])
    )
    dps = getattr(timing_points_state, "difficulty_points", [])
    sps = getattr(timing_points_state, "sample_points", [])
    eps = getattr(timing_points_state, "effect_points", [])

    for tp in tps:
        all_times.add(tp.time)
    for dp in dps:
        all_times.add(dp.time)
    for sp in sps:
        all_times.add(sp.time)
    for ep in eps:
        all_times.add(ep.time)

    sorted_times = sorted(list(all_times))
    last_props = None

    for time in sorted_times:
        tp = beatmap.timing_points.timing_point_at(time)
        dp = beatmap.timing_points.difficulty_point_at(time)
        sp = beatmap.timing_points.sample_point_at(time)
        ep = beatmap.timing_points.effect_point_at(time)

        is_timing = tp is not None and tp.time == time
        beat_len = tp.beat_len if tp else (-100.0 / (dp.slider_velocity if dp else 1.0))

        meter = tp.time_signature.numerator if tp else 4
        sample_set = sp.sample_bank.value if sp else 1
        sample_index = sp.custom_sample_bank if sp else 0
        volume = sp.sample_volume if sp else 100

        kiai = ep.kiai if ep else False
        omit_bar = tp.omit_first_bar_line if tp else False
        effect_flags = (1 if kiai else 0) | (8 if omit_bar else 0)

        current_props = (
            beat_len,
            meter,
            sample_set,
            sample_index,
            volume,
            effect_flags,
        )

        if is_timing:
            writer.write(
                f"{time},{beat_len},{meter},{sample_set},{sample_index},{volume},1,{effect_flags}\n"
            )
            last_props = (
                1.0,
                meter,
                sample_set,
                sample_index,
                volume,
                effect_flags,
            )  # velocity resets to 1.0
        else:
            if (
                last_props
                and abs(last_props[0] - beat_len) < 1e-7
                and last_props[1:] == current_props[1:]
            ):
                continue
            writer.write(
                f"{time},{beat_len},{meter},{sample_set},{sample_index},{volume},0,{effect_flags}\n"
            )
            last_props = current_props


def _encode_hit_objects(beatmap, writer) -> None:
    # Construção precisa das flags e curvas
    writer.write("[HitObjects]\n")

    for obj in beatmap.hit_objects.hit_objects:
        x, y = 0, 0
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

        # Calculate hitsound flag
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

        # Format float removing .0 if integer to match osu string exactly
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
    # A máquina de conversão da curva do slider (B|1:2|3:4)
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

    # Placeholder node samples
    nodes = slider.repeat_count + 2
    writer.write("0|" * (nodes - 1) + "0,")
    writer.write("0:0|" * (nodes - 1) + "0:0,")


def _write_sample_bank(writer, samples, banks_only: bool, mode: GameMode) -> None:
    # Lógica de seleção do banco de som com volume fallback
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
