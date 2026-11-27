"""Shared visual system for the topology explainer (Manim CE 0.19.x)."""

from manim import *

PAPER = "#F4F1E8"
INK = "#23272E"
INK_SOFT = "#5A6069"
RED = "#B4433A"
BLUE = "#2D5C8A"
GOLD = "#BE8A3E"
GRAY = "#9AA0A6"
FONT = "Noto Sans CJK SC"


def cn(text, size=40, color=INK, weight=NORMAL, **kw):
    """Chinese/CJK text with a font that actually has the glyphs."""
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kw)


def math(latex, size=44, color=INK, **kw):
    return MathTex(latex, font_size=size, color=color, **kw)


class Beat(Scene):
    """Scene with a controlled clock so every section lands on the narration."""

    def setup(self):
        self.camera.background_color = PAPER
        self._clock = 0.0
        self.timing = {}
        self.target = 0.0

    def load_timing(self, key):
        import json
        from pathlib import Path

        path = Path(__file__).parent / "timing.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.timing = data[key]
        self.target = self.timing["sec"]
        self.cues = self.timing["cues"]
        return self.timing

    # ---- clock helpers -------------------------------------------------
    def play_to(self, *anims, run_time=1.0):
        self._clock += run_time
        self.play(*anims, run_time=run_time)

    def at(self, t):
        """Idle until absolute time t (seconds from the section start)."""
        gap = t - self._clock
        if gap > 0.001:
            self.wait(gap)
            self._clock = t

    def cue(self, index):
        return self.cues[index]

    def hold_until_end(self):
        gap = self.target - self._clock
        if gap > 0.02:
            self.wait(gap)
            self._clock = self.target


def ring_belt(points, color=BLUE, radius_scale=1.0, dashed=True, width=3):
    """A dashed belt around a group of points (the 'neighbourhood tube')."""
    center = sum(points, ORIGIN) / len(points)
    width = max(abs(p[0] - center[0]) for p in points) * 2 + 1.0
    height = max(abs(p[1] - center[1]) for p in points) * 2 + 1.0
    belt = Ellipse(width=width * radius_scale, height=height * radius_scale,
                   color=color, stroke_width=width if False else 3)
    belt.move_to(center)
    if dashed:
        belt = DashedVMobject(belt, num_dashes=40)
    belt.set_stroke(width=3)
    return belt
