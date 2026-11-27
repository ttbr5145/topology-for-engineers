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
        tag = cn("第一集", 22, RED).move_to([0, -2.15, 0])
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

    def torus(self, color=GOLD):
        outer = Ellipse(width=2.2, height=1.3, color=color, stroke_width=5)
        inner = Ellipse(width=0.98, height=0.42, color=color, stroke_width=4)
        return VGroup(outer, inner)

    def cup(self, color=GOLD):
        body = RoundedRectangle(width=1.55, height=1.6, corner_radius=0.12, color=color, stroke_width=5)
        handle = Arc(radius=0.46, start_angle=-PI / 2.2, angle=PI * 1.15, color=color,
                     stroke_width=5).next_to(body, RIGHT, buff=-0.14)
        rim = Ellipse(width=1.55, height=0.34, color=color, stroke_width=4).move_to(
            body.get_top() + DOWN * 0.02)
        return VGroup(body, handle, rim)

    def construct(self):
        # ── 第一屏：绳结（一条闭合曲线）
        knot = self.knot().scale(1.15).move_to([0, 0.85, 0])
        kl = cn("绳结：一条闭合曲线", 26, GREY).move_to([0, -0.55, 0])
        self.beat(1, Create(knot), FadeIn(kl), run_time=1.5)
        loop = Circle(radius=1.2, color=BLUE, stroke_width=5).move_to([0, 0.85, 0])
        kl2 = cn("解开成环：曲线连续变形，没有断开", 26, GREY).move_to([0, -0.55, 0])
        self.beat(1, Transform(knot, loop), Transform(kl, kl2), run_time=1.6, lead=1.7)
        self.beat(2, FadeOut(knot), FadeOut(kl), run_time=0.6)

        # ── 第二屏：甜甜圈 → 马克杯（同一条轮廓线换形状）
        torus = self.torus().move_to([0, 0.85, 0])
        tl = cn("甜甜圈 → 马克杯：还是一条闭合曲线", 26, GREY).move_to([0, -0.55, 0])
        self.beat(2, FadeIn(torus), FadeIn(tl), run_time=1.0)
        cup = self.cup().move_to([0, 0.85, 0])
        self.beat(2, Transform(torus, cup), run_time=1.8, lead=1.2)
        self.beat(3, FadeOut(torus), FadeOut(tl), run_time=0.6)

        # ── 第三屏：翻开课本
        head = cn("翻开课本", 34, BLUE).move_to([-5.1, 2.05, 0])
        self.beat(3, FadeIn(head, shift=DOWN * 0.15), run_time=0.8)

        s1 = MathTex(r"2^{X}", tex_template=TEX, color=INK, font_size=52).move_to([-4.9, 1.05, 0])
        s2 = MathTex(r"\mathscr{C}", tex_template=TEX, color=INK, font_size=52).move_to([-3.6, 1.05, 0])
        s3 = MathTex(r"\tau", tex_template=TEX, color=INK, font_size=52).move_to([-2.4, 1.05, 0])
        l1 = cn("幂集", 18, GREY).next_to(s1, DOWN, buff=0.18)
        l2 = cn("集族", 18, GREY).next_to(s2, DOWN, buff=0.18)
        l3 = cn("拓扑", 18, GREY).next_to(s3, DOWN, buff=0.18)
        self.beat(3, FadeIn(s1), FadeIn(l1), run_time=0.7, lead=0.5)
        self.beat(3, FadeIn(s2), FadeIn(l2), run_time=0.7, lead=1.3)
        self.beat(3, FadeIn(s3), FadeIn(l3), run_time=0.7, lead=2.1)

        # ── 定义与定理（ε-δ 语言）
        rows = []
        d1 = cn("开集 U", 24, INK).move_to([-5.0, 0.3, 0])
        f1 = MathTex(r"\forall x\in U,\ \exists\,\varepsilon>0:\ B_{\varepsilon}(x)\subseteq U",
                     tex_template=TEX, font_size=26, color=INK).align_to(np.array([-1.55, 0.05, 0]), LEFT).set_y(0.3)
        d2 = cn("聚点 p", 24, INK).move_to([-5.0, -0.5, 0])
        f2 = MathTex(r"\forall\varepsilon>0:\ \left(B_{\varepsilon}(p)\setminus\{p\}\right)\cap A\neq\varnothing",
                     tex_template=TEX, font_size=26, color=INK).align_to(np.array([-1.55, -0.85, 0]), LEFT).set_y(-0.5)
        d3 = cn("粘结引理", 24, INK).move_to([-5.0, -1.3, 0])
        f3 = MathTex(r"f|_{A},\ f|_{B}\ \mathrm{cont.},\ A\cup B=X\ \Rightarrow\ f\ \mathrm{cont.}",
                     tex_template=TEX, font_size=26, color=INK).align_to(np.array([-1.55, -1.75, 0]), LEFT).set_y(-1.3)
        for g in [VGroup(d1, f1), VGroup(d2, f2), VGroup(d3, f3)]:
            rows.append(g)
        self.beat(4, FadeIn(rows[0]), run_time=0.8)
        self.beat(4, FadeIn(rows[1]), run_time=0.8, lead=1.1)
        self.beat(4, FadeIn(rows[2]), run_time=0.8, lead=2.2)

        ask = cn("读完十余页，仍不知它在研究什么", 26, INK).move_to([0, -1.72, 0])
        self.beat(5, FadeIn(ask), run_time=1.0)
        self.finish()


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

        self.beat(3, FadeOut(kw1), FadeOut(kw2), FadeOut(dwa), FadeOut(cross), FadeOut(note1),
                  run_time=0.7)
        note2 = cn("从排序走向拓扑体", 26, BLUE).move_to([0, -1.55, 0])
        self.beat(3, FadeIn(note2, shift=UP * 0.2), run_time=1.0, lead=0.7)
        self.finish()


class S6Queue(Base):
    seg_id = "s6"

    def construct(self):
        names = ["a", "b", "c", "d", "e"]
        colors = [BLUE, RED, TEAL, GOLD, "#A48BCB"]
        scatter = {"a": np.array([-4.3, 0.95, 0]), "b": np.array([-1.5, 1.55, 0]),
                   "c": np.array([1.3, 1.2, 0]), "d": np.array([3.9, 1.55, 0]),
                   "e": np.array([0.1, 0.35, 0])}
        groups = {}
        for i, ch in enumerate(names):
            dot = Dot([0, 0, 0], radius=0.18, color=colors[i])
            lbl = cn(ch, 30, colors[i]).next_to(dot, RIGHT, buff=0.1)
            groups[ch] = VGroup(dot, lbl).move_to(scatter[ch])

        slot_top = Line([-3.4, -0.55, 0], [3.6, -0.55, 0], color=LIGHT, stroke_width=2)
        slot_bot = Line([-3.4, -1.45, 0], [3.6, -1.45, 0], color=LIGHT, stroke_width=2)

        self.beat(1, LaggedStart(*[FadeIn(groups[c], scale=1.1) for c in names], lag_ratio=0.15),
                  run_time=1.5)
        self.beat(1, Create(slot_top), Create(slot_bot), run_time=0.8, lead=2.8)

        tip = cn("只知道谁在谁的前面 / 后面", 22, GREY).move_to([0, -1.95, 0])
        self.beat(2, FadeIn(tip), run_time=0.8)

        arrow = Arrow(groups["a"].get_right() + RIGHT * 0.05, groups["b"].get_left() + LEFT * 0.05,
                      color=RED, stroke_width=2.5, tip_length=0.16, buff=0.15)
        self.beat(3, Create(arrow), run_time=0.9)

        row_y = -1.0
        self.beat(4, groups["a"].animate.move_to([-0.55, row_y, 0]),
                  groups["b"].animate.move_to([0.55, row_y, 0]),
                  FadeOut(arrow), run_time=1.2)

        self.beat(5, groups["c"].animate.move_to([-1.85, row_y, 0]), run_time=0.9)

        arr2 = Arrow(groups["b"].get_right() + RIGHT * 0.05, groups["e"].get_left() + LEFT * 0.05,
                     color=RED, stroke_width=2.5, tip_length=0.16, buff=0.15)
        self.beat(6, groups["e"].animate.move_to([1.65, row_y, 0]), Create(arr2), run_time=0.9)
        self.beat(7, groups["d"].animate.move_to([2.85, row_y, 0]), FadeOut(arr2), run_time=0.9)

        col_x = -1.1
        ys = [1.75, 1.02, 0.28, -0.46, -1.2]
        order = ["c", "a", "b", "e", "d"]
        self.beat(8, *[groups[ch].animate.move_to([col_x, ys[k], 0]) for k, ch in enumerate(order)],
                  FadeOut(slot_top), FadeOut(slot_bot), FadeOut(tip), run_time=1.5)

        done = cn("顺序：c → a → b → e → d", 28, BLUE).move_to([2.6, 1.35, 0])
        done2 = cn("用位置关系完成排序", 26, INK).move_to([2.6, 0.55, 0])
        self.beat(8, FadeIn(done), FadeIn(done2), run_time=1.0, lead=1.6)
        note = cn("计算机中另有实现方式", 22, GREY).move_to([2.6, -0.35, 0])
        self.beat(9, FadeIn(note), run_time=0.8)
        note2 = cn("核心：位置关系", 26, RED).move_to([2.6, -1.15, 0])
        self.beat(10, FadeIn(note2, scale=1.1), run_time=0.9)
        self.finish()


class S7TopoBody(Base):
    seg_id = "s7"

    N = 6
    XS = np.linspace(-2.6, 2.6, N)

    def construct(self):
        amp = ValueTracker(0.0)
        squeeze = ValueTracker(1.0)
        phase = ValueTracker(0.0)
        lab = [MathTex(r"x_{%d}" % (i + 1), tex_template=TEX, font_size=24, color=BLUE)
               for i in range(self.N)]

        def px(i):
            return float(self.XS[i]) * squeeze.get_value()

        def py(x):
            return 0.5 + amp.get_value() * math.sin(phase.get_value() - x * 1.05)

        def pt(i):
            return np.array([px(i), py(px(i)), 0.0])

        def mk(i):
            g = VGroup(Dot(radius=0.09, color=BLUE), lab[i].copy())

            def upd(m, dt):
                p = pt(i)
                m[0].move_to(p)
                m[1].move_to(p + DOWN * 0.26)

            g.add_updater(upd)
            upd(g, 0)
            return g

        points = VGroup(*[mk(i) for i in range(self.N)])
        R = 0.58

        def link(i):
            a, b = pt(i), pt(i + 1)
            d = b - a
            ang = math.atan2(d[1], d[0])
            L = float(np.linalg.norm(d)) + 2 * R
            rect = RoundedRectangle(width=L, height=2 * R, corner_radius=R,
                                    color=TEAL, stroke_width=2.2)
            rect.set_fill(opacity=0)
            rect.rotate(ang)
            rect.move_to((a + b) / 2)
            return DashedVMobject(rect, num_dashes=44, dashed_ratio=0.45)

        links = [always_redraw(lambda i=i: link(i)) for i in range(self.N - 1)]

        head = cn("从点到邻域", 30, BLUE).move_to([0, 2.55, 0])
        sub = cn("一个点、一个小邻域，再一个点", 22, GREY).move_to([0, 2.1, 0])
        self.beat(1, FadeIn(head), run_time=0.8)
        self.beat(2, FadeIn(sub), run_time=0.7)

        self.beat(3, FadeIn(points[0]), run_time=0.8)
        n1 = Circle(radius=1.3, color=TEAL, stroke_width=2.5).move_to(pt(0))
        self.beat(3, GrowFromCenter(n1), run_time=1.0, lead=1.2)
        self.beat(3, FadeIn(points[1]), run_time=0.7, lead=2.4)
        self.beat(3, FadeOut(n1), FadeIn(links[0]), run_time=0.9, lead=3.6)

        n2 = Circle(radius=1.3, color=TEAL, stroke_width=2.5).move_to(pt(1))
        self.beat(4, GrowFromCenter(n2), run_time=0.9)
        self.beat(4, FadeIn(points[2]), run_time=0.7, lead=0.9)
        self.beat(4, FadeOut(n2), FadeIn(links[1]), run_time=0.9, lead=2.2)

        self.beat(5, LaggedStart(*[FadeIn(points[i]) for i in range(3, self.N)], lag_ratio=0.25),
                  run_time=1.0)
        self.beat(5, LaggedStart(*[FadeIn(links[i]) for i in range(2, self.N - 1)], lag_ratio=0.25),
                  run_time=1.2, lead=0.8)

        dirs = VGroup(cn("上", 20, GREY).move_to([0, 2.55, 0]), cn("下", 20, GREY).move_to([0, -0.6, 0]),
                      cn("左", 20, GREY).move_to([-6.1, 0.5, 0]), cn("右", 20, GREY).move_to([6.1, 0.5, 0]),
                      cn("前", 20, GREY).move_to([-4.8, 1.9, 0]), cn("后", 20, GREY).move_to([4.8, 1.9, 0]))
        self.beat(6, FadeIn(dirs), run_time=0.8)
        self.beat(6, FadeOut(dirs, scale=1.2), run_time=0.6, lead=1.9)

        phase.add_updater(lambda m, dt: m.increment_value(dt * 1.3))
        self.beat(7, amp.animate.set_value(0.55), run_time=1.2)
        self.wait(3.0)
        phase.clear_updaters()

        self.beat(8, amp.animate.set_value(0.0), run_time=0.8)
        self.beat(8, squeeze.animate.set_value(0.6), run_time=1.0, lead=0.9)
        self.beat(8, squeeze.animate.set_value(1.5), run_time=1.2, lead=2.2)
        self.play(squeeze.animate.set_value(1.0), run_time=0.8)
        self.finish()


class S8Deform(Base):
    seg_id = "s8"

    def cluster(self):
        dots = VGroup()
        links = VGroup()
        n = 6
        for i in range(n):
            a = -1.2 + 2.4 * i / (n - 1)
            dots.add(Dot([a, 0.0, 0], radius=0.09, color=BLUE))
        for i in range(n - 1):
            a = -1.2 + 2.4 * i / (n - 1)
            b = -1.2 + 2.4 * (i + 1) / (n - 1)
            rect = RoundedRectangle(width=(b - a) + 0.9, height=0.9, corner_radius=0.45,
                                    color=TEAL, stroke_width=2.2)
            rect.set_fill(opacity=0)
            rect.move_to([(a + b) / 2, 0, 0])
            links.add(DashedVMobject(rect, num_dashes=36, dashed_ratio=0.45))
        return VGroup(links, dots)

    def construct(self):
        chain = self.cluster().move_to([0, 0.35, 0])
        self.beat(1, FadeIn(chain), run_time=0.9)

        # 压成球：点向中心聚拢，链环收拢为一个有体积的球
        core = Circle(radius=1.0, color=TEAL, stroke_width=3, fill_color=TEAL, fill_opacity=0.26)
        hl = Arc(radius=0.62, start_angle=0.45, angle=1.5, color=INK, stroke_width=2)
        hl.move_to([0, 0.35, 0])
        ball = VGroup(core, hl).move_to([0, 0.35, 0])
        dots = chain[1]
        self.beat(1, *[d.animate.move_to([0, 0.35, 0]) for d in dots], run_time=1.4, lead=0.35)
        self.beat(1, FadeOut(chain[0]), FadeOut(dots), FadeIn(ball, scale=1.1),
                  run_time=1.2, lead=1.5)

        body = RoundedRectangle(width=2.2, height=1.2, corner_radius=0.42, color=TEAL,
                                stroke_width=3, fill_color=TEAL, fill_opacity=0.26)
        rim = Ellipse(width=2.0, height=0.38, color=TEAL, stroke_width=2)
        cyl = VGroup(body, rim).move_to([0, 0.35, 0])
        rim.move_to(cyl[0].get_top() + DOWN * 0.06)
        tri = Polygon([-0.85, -0.35, 0], [0.85, -0.35, 0], [0, 1.45, 0], color=TEAL,
                      stroke_width=3, fill_color=TEAL, fill_opacity=0.26)
        shade = Line([0.3, 0.55, 0], [0.3, 1.05, 0], color=INK, stroke_width=2)
        cone = VGroup(tri, shade).move_to([0, 0.05, 0])

        self.beat(2, Transform(ball, cyl), run_time=1.6)
        self.beat(2, Transform(ball, cone), run_time=1.8, lead=1.6)

        # 尝试闭合成环，但 x_n 不在 x_1 的邻域里，缺口合不上
        gap = 0.9
        loop = Arc(radius=1.0, start_angle=PI / 2 + gap, angle=TAU - 2 * gap, color=TEAL,
                   stroke_width=3).move_to([0, 0.35, 0])
        self.beat(3, Transform(ball, loop), run_time=1.6)

        p1 = Dot(loop.point_from_proportion(0.0), radius=0.09, color=BLUE)
        pn = Dot(loop.point_from_proportion(1.0), radius=0.09, color=RED)
        x1 = MathTex(r"x_1", tex_template=TEX, font_size=26, color=BLUE).next_to(p1, LEFT, buff=0.16)
        xn = MathTex(r"x_n", tex_template=TEX, font_size=26, color=RED).next_to(pn, RIGHT, buff=0.16)
        cross = cn("✕", 34, RED).move_to([0, 2.05, 0])

        self.beat(4, FadeIn(p1), FadeIn(pn), FadeIn(x1), FadeIn(xn), FadeIn(cross), run_time=1.0)
        why = cn("最后一点不在第一点的邻域里", 24, GREY).move_to([0, -1.2, 0])
        self.beat(5, FadeIn(why), run_time=0.9)

        keep = MathTex(r"d(x_1,x_n)>0", tex_template=TEX, font_size=30, color=INK).move_to([0, -1.66, 0])
        self.beat(5, FadeIn(keep), run_time=1.0, lead=1.2)
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

    def construct(self):
        outer = Ellipse(width=2.3, height=1.35, color=GOLD, stroke_width=5).move_to([0, 0.9, 0])
        inner = Ellipse(width=1.0, height=0.44, color=GOLD, stroke_width=4).move_to([0, 0.9, 0])
        lbl = cn("甜甜圈：一条闭合轮廓线", 24, GREY).move_to([0, -0.35, 0])
        self.beat(1, Create(outer), Create(inner), FadeIn(lbl), run_time=1.4)

        body = RoundedRectangle(width=1.6, height=1.65, corner_radius=0.14, color=GOLD,
                                stroke_width=5).move_to([0, 0.9, 0])
        self.beat(1, FadeOut(inner), Transform(outer, body),
                  Transform(lbl, cn("马克杯：还是同一条轮廓线", 24, GREY).move_to([0, -0.35, 0])),
                  run_time=1.8, lead=1.8)

        handle = Arc(radius=0.48, start_angle=-PI / 2.2, angle=PI * 1.15, color=GOLD,
                     stroke_width=5).next_to(body, RIGHT, buff=-0.12)
        rim = Ellipse(width=1.6, height=0.32, color=GOLD, stroke_width=4).move_to(
            body.get_top() + DOWN * 0.02)
        self.beat(1, Create(handle), Create(rim), run_time=1.2, lead=3.4)

        goal = cn("研究目标：由位置关系决定的几何性质", 28, INK).move_to([0, -1.55, 0])
        way = cn("研究方法：连续变形（同胚）", 26, BLUE).move_to([0, -2.1, 0])
        self.beat(2, FadeIn(goal), run_time=1.0)
        self.beat(2, FadeIn(way), run_time=0.9, lead=1.2)
        self.finish()


