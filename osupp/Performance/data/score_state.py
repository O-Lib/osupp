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

from .mode import GameMode


@dataclass(slots=True)
class ScoreState:
    max_combo: int = 0

    osu_large_tick_hits: int = 0
    osu_small_tick_hits: int = 0
    slider_end_hits: int = 0

    n_geki: int = 0
    n_katu: int = 0
    n300: int = 0
    n100: int = 0
    n50: int = 0
    misses: int = 0

    legacy_total_score: int | None = None

    def total_hits(self, mode: GameMode) -> int:
        amount = self.n300 + self.n100 + self.misses

        if mode != GameMode.TAIKO:
            amount += self.n50

            if mode != GameMode.OSU:
                amount += self.n_katu
                amount += (1 if mode != GameMode.CATCH else 0) * self.n_geki

        return amount
