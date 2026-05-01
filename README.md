<div align="center">

# OSUPP

**All-in-one Python library for osu! beatmap parsing, mod handling, and pp calculation. The only osu! lib you'll ever need.**

[![PyPI Version](https://img.shields.io/pypi/v/osupp?style=for-the-badge&color=pink)](https://pypi.org/project/osupp/)
[![Python](https://img.shields.io/pypi/pyversions/osupp?style=for-the-badge&color=blue)](https://pypi.org/project/osupp/)
[![License](https://img.shields.io/github/license/O-Lib/osupp?style=for-the-badge&color=green)](LICENSE)
[![Typing](https://img.shields.io/badge/typing-checked-blue?style=for-the-badge)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge&logo=pre-commit)](https://pre-commit.com/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-orange?style=for-the-badge)](https://docs.astral.sh/ruff/)
[![Discord](https://img.shields.io/discord/9p7whE7QxQ?style=for-the-badge&logo=discord&label=discord&color=5865F2)](https://discord.gg/9p7whE7QxQ)

</div>

---

### Features

- **Beatmap Parsing** - Full `.osu` file parsing including all sections: General, Metadata, Difficulty, Events, Timing Points, Hit Objects, Colors, and Editor
- **Mod Handling** - Complete mod system supporting all osu! game modes (osu!, Taiko, Catch, Mania) with legacy and modern mod representations
- **Performance Calculation** - PP calculation for all supported game modes *(in active development)*
- **Type-safe** - Fully typed codebase, mypy-checked

---

### Installation

```bash
pip install osupp
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add osupp
```

**Requires Python 3.10+**

---

### Quick Start

### Beatmap Parsing

```python
from osupp.Beatmap import Beatmap

beatmap = Beatmap.from_path("path/to/map.osu")

print(beatmap.metadata.title)
print(beatmap.metadata.version)
print(beatmap.difficulty.approach_rate)
print(beatmap.difficulty.circle_size)

for obj in beatmap.hit_objects.objects:
    print(obj)

for tp in beatmap.timing_points.control_points.timing_points:
    print(tp.bpm)
```

### Mod Handling

```python
from osupp.Mods import GameMods, GameMode, HardRockOsu, DoubleTimeOsu

mods = GameMods([HardRockOsu(), DoubleTimeOsu()])

# Legacy bitfield conversion
legacy = mods.to_legacy()
print(legacy.value)

# From acronym strings
mods = GameMods.from_acronyms(["HD", "DT"], GameMode.OSU)

# Intermode mods
from osupp.Mods import GameModsIntermode
intermode = GameModsIntermode.from_acronyms(["HD", "NC"])
```

---

### Project Structure

```
osupp/
├── Beatmap/ # .osu file parsing and encoding
│   ├── beatmap.py
│   ├── reader.py
│   ├── encode.py
│   └── section/ # Individual section parsers
│       ├── general.py
│       ├── metadata.py
│       ├── difficulty.py
│       ├── timing_points.py
│       ├── hit_objects/
│       └── ...
└── Mods/ # Mod system
    ├── game_mod.py
    ├── game_mods.py
    ├── game_mode.py
    ├── generated_mods.py
    └── ...
```

---

### Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

---

### Security

To report a security vulnerability, see [SECURITY.md](SECURITY.md).

---

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>

<p align="center">
        <code>&copy 2026-Present <a href="https://github.com/O-Lib">O!Lib Team</a></code>
</p>
