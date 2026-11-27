"""面向工科的拓扑学 · 序言 —— Manim 场景源码（1920x1080 / 24fps / 画面轨）。

时间全部由 timing.json 的实测旁白句子区间驱动：
每个场景只负责"在第几句开始时发生什么"，结尾自动补齐到段落总时长。
"""

import json
import math
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent

INK = "#EDE7D8"
BLUE = "#8FB4DE"
RED = "#E4735F"
GREY = "#93A3AE"
PAPER = "#101822"
LIGHT = "#37424F"
GOLD = "#D8B272"
TEAL = "#63B4A2"
CN = "Noto Sans CJK SC"

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{mathrsfs}")


def cn(text, size=32, color=INK, **kw):
    return Text(text, font=CN, font_size=size, color=color, **kw)


class Base(Scene):
    seg_id = "s1"

    def setup(self):
        self.camera.background_color = PAPER
        data = json.loads((ROOT / "timing.json").read_text(encoding="utf-8"))
        seg = data["segments"][self.seg_id]
        self.total = float(seg["seconds"])
        self.sent = seg["sentences"]

    def cue(self, i):
        return float(self.sent[i - 1]["start"])

    def hold(self, t):
        gap = t - self.time
        if gap > 1e-4:
            self.wait(gap)

    def beat(self, i, *anims, run_time=1.1, lead=0.0):
        """等到第 i 句开始（+lead），播放时不越过下一句太多。"""
        self.hold(self.cue(i) + lead)
        rt = run_time
        if i < len(self.sent):
            rt = min(rt, max(0.3, self.sent[i]["start"] - self.time + 0.5))
        self.play(*anims, run_time=rt)

    def finish(self):
        # 多留 0.25 秒静帧，保证成片裁切时素材帧数足够
        self.hold(self.total + 0.25)


class S1Cover(Base):
    seg_id = "s1"

    def construct(self):
        rule = Line(LEFT * 3.4, RIGHT * 3.4, color=LIGHT, stroke_width=2).move_to([0, 1.9, 0])
        title = cn("面向工科的拓扑学", 80, INK).move_to([0, 0.8, 0])
        subtitle = cn("序言：拓扑学在研究什么", 40, BLUE).move_to([0, -0.25, 0])
        rule2 = Line(LEFT * 2.1, RIGHT * 2.1, color=LIGHT, stroke_width=2).move_to([0, -1.0, 0])
        note = cn("简单直观   ·   诸多不严谨   ·   欢迎评论区补充", 26, GREY).move_to([0, -1.62, 0])
        tag = cn("第 0 集", 22, RED).move_to([0, -2.45, 0])
        mark = cn("TOPOLOGY  FOR  ENGINEERING", 20, GREY).move_to([0, 2.25, 0])

        self.beat(1, GrowFromCenter(rule), FadeIn(mark, shift=UP * 0.2), run_time=1.0, lead=0.35)
        self.beat(1, FadeIn(title, shift=UP * 0.35), run_time=1.3, lead=1.1)
        self.beat(2, FadeIn(subtitle, shift=UP * 0.2), GrowFromCenter(rule2), run_time=1.2)
        self.beat(3, FadeIn(note), FadeIn(tag), run_time=0.9)
        self.finish()


class S2Impression(Base):
    seg_id = "s2"

    def knot(self):
        def f(u):
            t = u * TAU
            return np.array([np.sin(t) + 2 * np.sin(2 * t), np.cos(t) - 2 * np.cos(2 * t), 0]) / 3.0

        return ParametricFunction(f, t_range=[0, 1], color=BLUE, stroke_width=5)

    def donut(self, color=GOLD):
        outer = Ellipse(width=2.0, height=1.25, color=color, stroke_width=5)
        inner = Ellipse(width=0.85, height=0.32, color=color, stroke_width=5)
        return VGroup(outer, inner)

    def cup(self, color=GOLD):
        body = RoundedRectangle(width=1.45, height=1.5, corner_radius=0.1,
                                color=color, stroke_width=5)
        handle = Arc(radius=0.42, start_angle=-PI / 2.2, angle=PI * 1.15, color=color,
                     stroke_width=5).next_to(body, RIGHT, buff=-0.12)
        rim = Ellipse(width=1.45, height=0.34, color=color, stroke_width=5).move_to(
            body.get_top() + DOWN * 0.02)
        return VGroup(body, handle, rim)

    def construct(self):
        axis = Line(UP * 3.4, DOWN * 3.4, color=LIGHT, stroke_width=2)
        self.add(axis)

        knot = self.knot().scale(0.95).move_to([-3.55, 1.15, 0])
        knot_lbl = cn("绳结", 26, GREY).next_to(knot, DOWN, buff=0.35)
        donut = self.donut().scale(0.75).move_to([3.55, 1.15, 0])
        donut_lbl = cn("甜甜圈 · 马克杯", 26, GREY).next_to(donut, DOWN, buff=0.35)

        self.beat(1, Create(knot), FadeIn(knot_lbl), run_time=1.4)
        loop = Circle(radius=1.0, color=BLUE, stroke_width=5).move_to(knot)
        self.beat(1, Transform(knot, loop),
                  Transform(knot_lbl, cn("解开成环", 26, GREY).move_to(knot_lbl)),
                  run_time=1.2, lead=1.4)

        self.beat(2, FadeIn(donut), FadeIn(donut_lbl), run_time=1.2)
        cup = self.cup().scale(0.75).move_to(donut)
        self.beat(2, Transform(donut, cup), run_time=1.6, lead=1.6)

        head = cn("翻开课本", 30, BLUE).move_to([-4.0, -0.72, 0])
        sym1 = MathTex(r"2^{X}", tex_template=TEX, color=INK, font_size=48).move_to([-4.95, -1.6, 0])
        sym2 = MathTex(r"\mathscr{C}", tex_template=TEX, color=INK, font_size=48).move_to([-3.95, -1.6, 0])
        sym3 = MathTex(r"\tau", tex_template=TEX, color=INK, font_size=48).move_to([-3.1, -1.6, 0])
        l1 = cn("幂集", 18, GREY).next_to(sym1, DOWN, buff=0.2)
        l2 = cn("集族", 18, GREY).next_to(sym2, DOWN, buff=0.2)
        l3 = cn("拓扑", 18, GREY).next_to(sym3, DOWN, buff=0.2)

        self.beat(3, FadeIn(head), run_time=0.8)
        self.beat(3, FadeIn(sym1), FadeIn(l1), run_time=0.8, lead=0.55)
        self.beat(3, FadeIn(sym2), FadeIn(l2), run_time=0.8, lead=1.5)
        self.beat(3, FadeIn(sym3), FadeIn(l3), run_time=0.8, lead=2.4)

        card1 = self.card("开集的定义", [-1.78, -2.3, 0])
        card2 = self.card("聚点的定义", [0.02, -2.3, 0])
        card3 = self.card("粘结引理", [1.72, -2.3, 0])
        self.beat(4, FadeIn(card1), run_time=0.7)
        self.beat(4, FadeIn(card2), run_time=0.7, lead=0.9)
        self.beat(4, FadeIn(card3), run_time=0.7, lead=1.9)

        q = cn("？", 110, RED).move_to([4.4, -1.9, 0])
        ask = cn("读完十余页", 24, GREY).next_to(q, UP, buff=0.25)
        self.beat(5, FadeIn(q, scale=1.4), FadeIn(ask), run_time=1.1)
        self.finish()

    def card(self, text, pos):
        txt = cn(text, 22, INK)
        box = RoundedRectangle(width=max(1.55, txt.width + 0.4), height=0.62, corner_radius=0.08,
                               color=LIGHT, fill_color="#18232F", fill_opacity=1, stroke_width=1.5)
        box.move_to(pos)
        txt.move_to(pos)
        return VGroup(box, txt)


class S3Word(Base):
    seg_id = "s3"

    def construct(self):
        zh = cn("拓扑", 116, INK).move_to([0, 1.5, 0])
        en = cn("topology", 62, GREY).move_to([0, 0.0, 0])
        self.beat(1, FadeIn(zh, shift=UP * 0.3), run_time=1.2)
        self.beat(2, FadeIn(en), run_time=0.9)

        topo = cn("topo", 58, BLUE).move_to([-1.55, 0.0, 0])
        dash = cn("-", 58, INK).move_to([0, 0.0, 0])
        logy = cn("logy", 58, BLUE).move_to([1.45, 0.0, 0])
        self.beat(3, FadeOut(en), FadeIn(topo), FadeIn(dash), FadeIn(logy), run_time=1.2)

        pos_lbl = cn("位置", 34, RED).move_to([-1.55, -1.0, 0])
        sub_lbl = cn("学科", 34, RED).move_to([1.45, -1.0, 0])
        self.beat(4, FadeIn(pos_lbl, shift=UP * 0.2), FadeIn(sub_lbl, shift=UP * 0.2), run_time=1.0)
        self.beat(4, FadeOut(pos_lbl), FadeOut(sub_lbl),
                  Transform(topo, cn("位置", 58, RED).move_to([-1.55, 0.0, 0])),
                  Transform(logy, cn("学科", 58, RED).move_to([1.45, 0.0, 0])),
                  run_time=0.9, lead=0.9)

        merged = cn("研究位置的学科", 44, INK).move_to([0, 0.0, 0])
        self.beat(5, FadeOut(topo), FadeOut(dash), FadeOut(logy), FadeIn(merged), run_time=1.2)

        conclusion = cn("拓扑学 = 研究位置的学科", 44, BLUE).move_to([0, -1.2, 0])
        self.beat(5, FadeIn(conclusion, shift=UP * 0.2), run_time=1.1, lead=2.2)
        self.finish()


class S4Branches(Base):
    seg_id = "s4"

    def construct(self):
        root = cn("现代数学", 34, INK).move_to([0, 3.0, 0])
        root_box = RoundedRectangle(width=2.2, height=0.8, corner_radius=0.08,
                                    color=BLUE, fill_color="#1C2836", fill_opacity=1, stroke_width=2)
        root_box.move_to(root)
        ana = cn("分析", 30, INK).move_to([-4.6, 1.35, 0])
        alg = cn("代数", 30, INK).move_to([0, 1.35, 0])
        geo = cn("几何", 30, INK).move_to([4.6, 1.35, 0])
        lines = VGroup(
            Line(root_box.get_bottom() + DOWN * 0.02, ana.get_top() + UP * 0.12, color=LIGHT, stroke_width=2),
            Line(root_box.get_bottom() + DOWN * 0.02, alg.get_top() + UP * 0.12, color=LIGHT, stroke_width=2),
            Line(root_box.get_bottom() + DOWN * 0.02, geo.get_top() + UP * 0.12, color=LIGHT, stroke_width=2),
        )

        self.beat(1, FadeIn(root_box), FadeIn(root), run_time=1.0)
        self.beat(1, Create(lines), FadeIn(ana), run_time=0.9, lead=0.8)
        self.beat(1, FadeIn(alg), run_time=0.6, lead=1.6)
        self.beat(1, FadeIn(geo), run_time=0.6, lead=2.1)

        topo = cn("拓扑", 34, RED).move_to([5.9, -0.35, 0])
        dots_g = cn("⋯", 30, GREY).move_to([3.35, -0.35, 0])
        dots_a = cn("⋯", 30, GREY).move_to([-4.6, -0.35, 0])
        dots_b = cn("⋯", 30, GREY).move_to([0, -0.35, 0])
        l1 = Line(geo.get_bottom() + DOWN * 0.05, topo.get_top() + UP * 0.1, color=RED, stroke_width=2)
        l2 = Line(geo.get_bottom() + DOWN * 0.05, dots_g.get_top() + UP * 0.1, color=LIGHT, stroke_width=2)
        l3 = Line(ana.get_bottom() + DOWN * 0.05, dots_a.get_top() + UP * 0.1, color=LIGHT, stroke_width=2)
        l4 = Line(alg.get_bottom() + DOWN * 0.05, dots_b.get_top() + UP * 0.1, color=LIGHT, stroke_width=2)

        self.beat(1, Create(l1), FadeIn(topo), run_time=1.0, lead=2.9)
        self.beat(1, Create(l2), FadeIn(dots_g), Create(l3), FadeIn(dots_a),
                  Create(l4), FadeIn(dots_b), run_time=1.0, lead=3.6)

        box = RoundedRectangle(width=1.85, height=0.78, corner_radius=0.08,
                               color=RED, stroke_width=2.5).move_to(topo)
        note = cn("只研究由位置关系决定的几何性质", 30, INK).move_to([0, -2.15, 0])
        self.beat(2, ShowPassingFlash(box.copy().set_stroke(RED, 6), time_width=0.5),
                  FadeIn(box), run_time=1.0)
        self.beat(2, FadeIn(note, shift=UP * 0.2), run_time=1.0, lead=1.4)
        self.finish()


class S5Sort(Base):
    seg_id = "s5"

    def construct(self):
        title = cn("拓扑排序", 42, INK).move_to([0, 3.3, 0])
        sub = cn("Topological Sort", 22, GREY).move_to([0, 2.5, 0])

        pos = {"a": np.array([-2.6, 1.55, 0]), "b": np.array([-0.4, 1.55, 0]),
               "c": np.array([-2.6, 0.2, 0]), "e": np.array([0.2, 0.2, 0]),
               "d": np.array([2.2, 0.2, 0])}
        nodes = VGroup()
        for ch, p in pos.items():
            dot = Dot(p, radius=0.15, color=BLUE)
            lbl = cn(ch, 30, BLUE).next_to(dot, UP, buff=0.1)
            nodes.add(VGroup(dot, lbl))
        edges = VGroup(
            Arrow(pos["c"] + UP * 0.28, pos["a"] + DOWN * 0.28, buff=0.18, color=GREY,
                  stroke_width=2.2, tip_length=0.15),
            Arrow(pos["a"] + RIGHT * 0.3, pos["b"] + LEFT * 0.3, buff=0.18, color=GREY,
                  stroke_width=2.2, tip_length=0.15),
            Arrow(pos["a"] + DOWN * 0.28, pos["e"] + UP * 0.28, buff=0.18, color=GREY,
                  stroke_width=2.2, tip_length=0.15),
            Arrow(pos["e"] + RIGHT * 0.3, pos["d"] + LEFT * 0.3, buff=0.18, color=GREY,
                  stroke_width=2.2, tip_length=0.15),
        )

        self.beat(1, FadeIn(title, shift=DOWN * 0.2), FadeIn(sub), run_time=1.0)
        self.beat(1, LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nodes], lag_ratio=0.2),
                  run_time=1.4, lead=1.0)
        self.beat(1, LaggedStart(*[Create(e) for e in edges], lag_ratio=0.25),
                  run_time=1.6, lead=2.2)

        kw1 = cn("拓扑排序", 30, INK).move_to([-1.9, -1.25, 0])
        kw2 = cn("拓扑学", 30, INK).move_to([1.9, -1.25, 0])
        dwa = DashedLine([-0.45, -1.25, 0], [0.45, -1.25, 0], color=RED, stroke_width=3)
        cross = VGroup(
            Line([-0.16, -1.41, 0], [0.16, -1.09, 0], color=RED, stroke_width=4),
            Line([-0.16, -1.09, 0], [0.16, -1.41, 0], color=RED, stroke_width=4),
        )
        note1 = cn("仅字面上的关系", 24, GREY).move_to([0, -1.95, 0])
        self.beat(2, FadeIn(kw1), FadeIn(kw2), Create(dwa), Create(cross), FadeIn(note1),
                  run_time=1.2)

        note2 = cn("从排序走向拓扑体", 26, BLUE).move_to([0, -2.7, 0])
        self.beat(3, FadeIn(note2, shift=UP * 0.2), run_time=1.0)
        self.finish()


class S6Queue(Base):
    seg_id = "s6"

    def construct(self):
        names = ["a", "b", "c", "d", "e"]
        colors = [BLUE, RED, TEAL, GOLD, "#A48BCB"]
        scatter = {"a": np.array([-4.3, 1.7, 0]), "b": np.array([-1.5, 2.4, 0]),
                   "c": np.array([1.3, 2.0, 0]), "d": np.array([3.9, 2.4, 0]),
                   "e": np.array([0.1, 0.7, 0])}
        groups = {}
        for i, ch in enumerate(names):
            dot = Dot([0, 0, 0], radius=0.19, color=colors[i])
            lbl = cn(ch, 32, colors[i]).next_to(dot, RIGHT, buff=0.12)
            groups[ch] = VGroup(dot, lbl).move_to(scatter[ch])

        slot_top = Line([-3.4, -1.05, 0], [3.6, -1.05, 0], color=LIGHT, stroke_width=2)
        slot_bot = Line([-3.4, -2.0, 0], [3.6, -2.0, 0], color=LIGHT, stroke_width=2)

        self.beat(1, LaggedStart(*[FadeIn(groups[c], scale=1.1) for c in names], lag_ratio=0.15),
                  run_time=1.5)
        # 向上平移，队列两条横线渐显
        self.beat(1, *[groups[c].animate.shift(UP * 1.3) for c in names], run_time=0.8, lead=2.0)
        self.beat(1, Create(slot_top), Create(slot_bot), run_time=0.8, lead=2.8)

        tip = cn("只知道谁在谁的前面 / 后面", 22, GREY).move_to([0, -2.65, 0])
        self.beat(2, FadeIn(tip), run_time=0.8)

        # a 说：b 在我的后面
        arrow = Arrow(groups["a"].get_right() + RIGHT * 0.05, groups["b"].get_left() + LEFT * 0.05,
                      color=RED, stroke_width=2.5, tip_length=0.16, buff=0.15)
        self.beat(3, Create(arrow), run_time=0.9)

        row_y = -1.55
        self.beat(4, groups["a"].animate.move_to([-0.55, row_y, 0]),
                  groups["b"].animate.move_to([0.55, row_y, 0]),
                  FadeOut(arrow), run_time=1.2)

        self.beat(5, groups["c"].animate.move_to([-1.85, row_y, 0]), run_time=0.9)
        self.beat(6, groups["e"].animate.move_to([1.65, row_y, 0]), run_time=0.9)
        self.beat(7, groups["d"].animate.move_to([2.85, row_y, 0]), run_time=0.9)

        # 排好顺序：横排转竖排、左对齐
        col_x = -1.1
        ys = [2.15, 1.05, -0.1, -1.2, -2.3]
        order = ["c", "a", "b", "e", "d"]
        self.beat(8, *[groups[ch].animate.move_to([col_x, ys[k], 0]) for k, ch in enumerate(order)],
                  FadeOut(slot_top), FadeOut(slot_bot), FadeOut(tip), run_time=1.5)

        done = cn("顺序：c → a → b → e → d", 28, BLUE).move_to([2.9, 1.2, 0])
        done2 = cn("用位置关系完成排序", 26, INK).move_to([3.0, 0.2, 0])
        self.beat(8, FadeIn(done), FadeIn(done2), run_time=1.0, lead=1.6)
        note = cn("计算机中另有实现方式", 22, GREY).move_to([3.0, -0.9, 0])
        self.beat(9, FadeIn(note), run_time=0.8)
        note2 = cn("核心：位置关系", 26, RED).move_to([3.0, -1.9, 0])
        self.beat(10, FadeIn(note2, scale=1.1), run_time=0.9)
        self.finish()


class S7TopoBody(Base):
    seg_id = "s7"

    XS = np.linspace(-2.5, 2.5, 6)

    def construct(self):
        labels = [MathTex(r"x_{%d}" % (i + 1), tex_template=TEX, font_size=28, color=BLUE)
                  for i in range(6)]
        amp = ValueTracker(0.0)
        squeeze = ValueTracker(1.0)
        phase = ValueTracker(0.0)
        state = {"n": 1}

        def y_of(x):
            return 0.75 + amp.get_value() * np.sin(phase.get_value() - x * 1.2)

        def x_of(i):
            return self.XS[i] * squeeze.get_value()

        def make_point(i):
            d = Dot([x_of(i), y_of(x_of(i)), 0], radius=0.10, color=BLUE)
            lb = labels[i].copy()
            g = VGroup(d, lb)

            def upd(m, dt):
                xx = x_of(i)
                m[0].move_to([xx, y_of(xx), 0])
                m[1].move_to([xx, y_of(xx) - 0.42, 0])

            g.add_updater(upd)
            upd(g, 0)
            return g

        def belt():
            n = state["n"]
            if n < 2:
                return VGroup()
            pts = [(x_of(i), y_of(x_of(i))) for i in range(n)]
            xmin = min(p[0] for p in pts) - 0.55
            xmax = max(p[0] for p in pts) + 0.55
            ymin = min(p[1] for p in pts) - 0.95
            ymax = max(p[1] for p in pts) + 0.55
            rect = RoundedRectangle(width=xmax - xmin, height=ymax - ymin, corner_radius=0.48,
                                    color=TEAL, stroke_width=3)
            rect.move_to([(xmin + xmax) / 2, (ymin + ymax) / 2, 0])
            return DashedVMobject(rect, num_dashes=36, dashed_ratio=0.5)

        belt_obj = always_redraw(belt)
        points = [make_point(i) for i in range(6)]

        head = cn("从点到邻域", 28, BLUE).move_to([0, 3.4, 0])
        sub = cn("一个点，一个邻域，再一个点", 22, GREY).move_to([0, 2.95, 0])
        self.beat(1, FadeIn(head), run_time=0.8)
        self.beat(2, FadeIn(sub), run_time=0.7)

        self.beat(3, FadeIn(points[0], shift=UP * 0.1), run_time=0.9)
        ring = Circle(radius=0.92, color=TEAL, stroke_width=3).move_to(points[0][0])
        self.beat(3, GrowFromCenter(ring), run_time=1.0, lead=1.5)
        self.beat(3, FadeIn(points[1], shift=RIGHT * 0.2), run_time=0.9, lead=3.4)
        state["n"] = 2
        self.beat(3, FadeOut(ring), FadeIn(belt_obj), run_time=1.0, lead=4.8)

        self.beat(4, FadeIn(points[2], shift=RIGHT * 0.2), run_time=0.9)
        state["n"] = 3
        self.wait(0.1)

        self.beat(5, FadeIn(VGroup(*points[3:]), shift=RIGHT * 0.2), run_time=1.2)
        state["n"] = 6
        self.wait(0.1)

        dirs = VGroup(cn("上", 22, GREY).move_to([0, 2.4, 0]), cn("下", 22, GREY).move_to([0, -0.6, 0]),
                      cn("左", 22, GREY).move_to([-6.0, 0.75, 0]), cn("右", 22, GREY).move_to([6.0, 0.75, 0]),
                      cn("前", 22, GREY).move_to([-4.7, 2.1, 0]), cn("后", 22, GREY).move_to([4.7, 2.1, 0]))
        self.beat(6, FadeIn(dirs), run_time=0.9)
        self.beat(6, FadeOut(dirs, scale=1.3), run_time=0.6, lead=1.9)

        # 流动：相位持续推进，点与传送带一起波动
        phase.add_updater(lambda m, dt: m.increment_value(dt * 1.5))
        self.beat(7, amp.animate.set_value(0.62), run_time=1.2)
        self.wait(3.4)
        phase.clear_updaters()

        # 远近、疏密：横向拉伸与压缩
        self.beat(8, amp.animate.set_value(0.0), run_time=0.8)
        self.beat(8, squeeze.animate.set_value(0.68), run_time=1.1, lead=0.9)
        self.beat(8, squeeze.animate.set_value(1.32), run_time=1.3, lead=2.2)
        self.wait(1.0)
        self.play(squeeze.animate.set_value(1.0), run_time=0.9)
        self.finish()


class S8Deform(Base):
    seg_id = "s8"

    def ball(self):
        ball = Circle(radius=1.02, color=TEAL, fill_color=TEAL, fill_opacity=0.26, stroke_width=3)
        dots = VGroup(*[Dot([1.02 * math.cos(a), 1.02 * math.sin(a), 0], radius=0.09, color=BLUE)
                        for a in np.linspace(0, TAU, 6, endpoint=False)])
        return VGroup(ball, dots)

    def cylinder(self):
        body = RoundedRectangle(width=3.0, height=1.5, corner_radius=0.72, color=TEAL,
                                fill_color=TEAL, fill_opacity=0.26, stroke_width=3)
        dots = VGroup()
        for x in [-1.1, -0.55, 0.0, 0.55, 1.1]:
            dots.add(Dot([x, 0.42, 0], radius=0.09, color=BLUE))
            dots.add(Dot([x, -0.42, 0], radius=0.09, color=BLUE))
        return VGroup(body, dots)

    def cone(self):
        body = Triangle(color=TEAL, fill_color=TEAL, fill_opacity=0.26, stroke_width=3).scale(1.35)
        dots = VGroup(*[Dot([0.52 * (1 - abs(v)), v, 0], radius=0.09, color=BLUE)
                        for v in [-0.78, -0.3, 0.2, 0.68]])
        return VGroup(body, dots)

    def ring(self):
        body = Arc(radius=1.02, start_angle=0.4, angle=TAU - 0.8, color=RED, stroke_width=3)
        dots = VGroup(*[Dot([1.02 * math.cos(a), 1.02 * math.sin(a), 0], radius=0.09, color=BLUE)
                        for a in np.linspace(0.55, TAU - 0.55, 6)])
        gap = VGroup(Line([0.94, -0.12, 0], [1.16, 0.2, 0], color=RED, stroke_width=4),
                     Line([0.94, 0.2, 0], [1.16, -0.12, 0], color=RED, stroke_width=4))
        return VGroup(body, dots, gap)

    def construct(self):
        head = cn("同一列点，形状可以这样变", 28, BLUE).move_to([-3.4, 3.35, 0])
        self.beat(1, FadeIn(head), run_time=0.8)

        sphere = self.ball().move_to([-4.6, 0.85, 0])
        self.beat(1, FadeIn(sphere, scale=0.9), run_time=1.2)
        self.beat(1, FadeIn(cn("球", 26, GREY).move_to([-4.6, -0.62, 0])), run_time=0.6, lead=1.8)

        cyl = self.cylinder().scale(0.72).move_to([0.6, 1.55, 0])
        self.beat(2, FadeIn(cyl, scale=0.9), run_time=1.1)
        self.beat(2, FadeIn(cn("柱", 26, GREY).move_to([0.6, 0.55, 0])), run_time=0.6, lead=1.4)

        cone = self.cone().scale(0.8).move_to([4.5, 1.5, 0])
        self.beat(2, FadeIn(cone, scale=0.9), run_time=1.0, lead=2.6)
        self.beat(2, FadeIn(cn("锥", 26, GREY).move_to([4.5, 0.5, 0])), run_time=0.6, lead=3.6)

        loop = self.ring().scale(0.85).move_to([1.1, -1.95, 0])
        self.beat(3, FadeIn(loop, scale=0.95), run_time=1.1)
        self.beat(3, FadeIn(cn("环？", 28, RED).move_to([3.4, -1.95, 0])), run_time=0.7, lead=1.3)

        gap_lbl = cn("x₁ 与 xₙ 不在彼此的邻域里", 20, RED).move_to([1.1, -3.1, 0])
        self.beat(4, FadeIn(gap_lbl), run_time=0.8)
        self.beat(5, FadeIn(cn("必须保持一段距离", 24, INK).move_to([-4.6, -1.95, 0])), run_time=0.8)
        self.finish()


class S9Homeo(Base):
    seg_id = "s9"

    def construct(self):
        ok = cn("连续变形", 44, BLUE).move_to([-3.4, 1.85, 0])
        bad1 = cn("切割", 38, GREY).move_to([3.2, 2.2, 0])
        bad2 = cn("粘连", 38, GREY).move_to([3.2, 1.25, 0])
        self.beat(1, FadeIn(ok, shift=UP * 0.2), run_time=1.0)
        self.beat(1, FadeIn(bad1), FadeIn(bad2), run_time=0.9, lead=1.2)

        x1 = Line(bad1.get_corner(DR) + LEFT * 0.08, bad1.get_corner(UL) + RIGHT * 0.08,
                  color=RED, stroke_width=5)
        x2 = Line(bad2.get_corner(DR) + LEFT * 0.08, bad2.get_corner(UL) + RIGHT * 0.08,
                  color=RED, stroke_width=5)
        self.beat(1, Create(x2), run_time=0.5, lead=2.1)
        self.beat(2, Create(x1), run_time=0.5)

        sep = Line([-0.9, 2.5, 0], [-0.9, 0.3, 0], color=LIGHT, stroke_width=2)
        self.add(sep)

        name = cn("同胚映射", 58, INK).move_to([0, -0.7, 0])
        en = cn("homeomorphism", 24, GREY).move_to([0, -1.4, 0])
        self.beat(3, FadeIn(name, shift=UP * 0.25), FadeIn(en), run_time=1.2)
        self.beat(3, ShowPassingFlash(Rectangle(width=4.2, height=1.55, color=GOLD, stroke_width=3)
                                      .move_to([0, -1.05, 0]), time_width=0.6), run_time=0.8, lead=1.7)

        left = Circle(radius=0.58, color=TEAL, stroke_width=3).move_to([-3.5, -2.55, 0])
        right = RoundedRectangle(width=1.55, height=0.82, corner_radius=0.4, color=TEAL,
                                 stroke_width=3).move_to([3.5, -2.55, 0])
        eq = cn("同胚", 28, RED).move_to([0, -2.35, 0])
        arr1 = Arrow([-2.85, -2.35, 0], [-0.72, -2.35, 0], buff=0.0, color=RED,
                     stroke_width=2.5, tip_length=0.16)
        arr2 = Arrow([0.72, -2.35, 0], [2.85, -2.35, 0], buff=0.0, color=RED,
                     stroke_width=2.5, tip_length=0.16)
        self.beat(4, FadeIn(left), FadeIn(right), run_time=1.0)
        self.beat(4, Create(arr1), Create(arr2), FadeIn(eq), run_time=1.2, lead=0.9)

        rev = cn("（可逆）", 22, GREY).move_to([0, -3.15, 0])
        self.beat(4, FadeIn(rev), run_time=0.7, lead=2.6)

        end = cn("拓扑学研究这类拓扑体", 32, BLUE).move_to([0, 3.3, 0])
        self.beat(5, FadeIn(end, shift=DOWN * 0.2), run_time=1.0)
        self.finish()


class S10Donut(Base):
    seg_id = "s10"

    def donut(self):
        return VGroup(Ellipse(width=2.3, height=1.45, color=GOLD, stroke_width=5),
                      Ellipse(width=1.0, height=0.4, color=GOLD, stroke_width=5))

    def cup(self):
        body = RoundedRectangle(width=1.7, height=1.7, corner_radius=0.12, color=GOLD, stroke_width=5)
        handle = Arc(radius=0.5, start_angle=-PI / 2.2, angle=PI * 1.1, color=GOLD,
                     stroke_width=5).next_to(body, RIGHT, buff=-0.14)
        rim = Ellipse(width=1.7, height=0.38, color=GOLD, stroke_width=5).move_to(body.get_top())
        return VGroup(body, handle, rim)

    def construct(self):
        d = self.donut().scale(0.95).move_to([-3.2, 0.95, 0])
        lbl = cn("甜甜圈", 26, GREY).next_to(d, DOWN, buff=0.4)
        self.beat(1, FadeIn(d), FadeIn(lbl), run_time=1.0)
        c = self.cup().scale(0.95).move_to([2.5, 0.95, 0])
        self.beat(1, Transform(d, c), Transform(lbl, cn("咖啡杯", 26, GREY).move_to([2.5, -0.5, 0])),
                  run_time=2.4, lead=1.0)

        same = cn("同胚", 34, RED).move_to([-0.4, 0.95, 0])
        self.beat(1, FadeIn(same, scale=1.2), run_time=0.9, lead=3.8)

        goal = cn("研究目标：由位置关系决定的几何性质", 32, INK).move_to([0, -1.7, 0])
        way = cn("研究方法：连续变形（同胚）", 30, BLUE).move_to([0, -2.4, 0])
        self.beat(2, FadeIn(goal, shift=UP * 0.2), run_time=1.0)
        self.beat(2, FadeIn(way, shift=UP * 0.2), run_time=0.9, lead=1.0)

        end = VGroup(cn("序言", 40, INK), cn("面向工科的拓扑学", 22, GREY)).arrange(DOWN, buff=0.3)
        end.move_to([0, -1.9, 0])
        self.beat(2, FadeOut(goal), FadeOut(way), FadeIn(end, shift=UP * 0.2), run_time=1.0, lead=2.9)
        self.finish()


