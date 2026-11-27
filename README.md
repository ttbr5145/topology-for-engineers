# 面向工科的拓扑学

**用代码讲数学：把拓扑学讲稿做成带旁白与字幕的讲解动画。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.0-blue.svg)](https://github.com/ttbr5145/topology-for-engineers/tags)
[![Manim](https://img.shields.io/badge/Manim-Community%200.19-9cf.svg)](https://www.manim.community/)

写给工科生的拓扑学入门系列。每一集一个文件夹：讲稿、台词、场景源码、配音、成片同放一处，改一句台词就能重出一版。

## 分集

| 集 | 标题 | 状态 | 时长 |
| --- | --- | --- | --- |
| 第一集 | 序言：面向工科的拓扑学 | v1.0 已完成 | 3 分 44.8 秒 |
| 第二集 | 待定 | 空目录 | — |
| 第三集 | 待定 | 空目录 | — |

## 第一集：序言

- 1920×1080 / 24 fps / 5395 帧 / 224.8 秒
- 48 句旁白（单一男声），48 条字幕烧录进画面
- 音量标准化 −14.1 LUFS，峰值 −1.45 dBTP
- 10 个 Manim 场景，按逐句实测配音时长切分对齐

画面分十段：

| 段 | 场景 | 内容 |
| --- | --- | --- |
| 1 | `S1Cover` | 片头：面向工科的拓扑学 |
| 2 | `S2Impression` | 第一印象：绳结解开的环、甜甜圈与马克杯 |
| 3 | `S3Word` | 词源：位置（τοπος）+ 研究（λογος） |
| 4 | `S4Branches` | 两个分支：橡皮几何、拓扑排序 |
| 5 | `S5Sort` | 排序：c → a → b → e → d 的位置关系推演 |
| 6 | `S6Queue` | 五人排队 → 点列 x₁…xₙ 与「传送带」邻域 |
| 7 | `S7TopoBody` | 压成球、柱、锥；不能成环 |
| 8 | `S8Deform` | 连续变形 vs 切割、粘连 |
| 9 | `S9Homeo` | 同胚映射的定义 |
| 10 | `S10Donut` | 甜甜圈变成咖啡杯，收束研究目标与方法 |

## 目录

```
第一集/
├── 序言讲稿.txt              原始讲稿
├── script.json               48 句台词（voice_text 记录读音替换）
├── scenes/math/
│   ├── scene.py              10 个 Scene 源码
│   ├── common.py             配色、中文文本、节拍基类
│   ├── timing.json           逐段帧数 + 逐句相对时间
│   ├── video-config.json     分辨率与帧率
│   ├── render-profile.json   渲染档位
│   └── requirements.txt
├── scripts/
│   ├── fetch_voice.py        下载 48 条配音并转 48 kHz 单声道
│   ├── make_timing.py        按实测配音排时间表
│   ├── render_all.py         逐段渲染并校验帧数
│   └── make_composition.py   生成合成计划
├── audio/
│   ├── voice-urls.json       48 句配音地址
│   ├── voice-manifest.json   首句静默与句间停顿
│   └── voice-v1/             narration.wav + captions.json
├── renders/                  10 段分段画面
├── fonts/ （未入库：Noto Sans SC，OFL 1.1，从 Google Fonts 取回）
├── composition.json          合成计划
├── out/                      成片与渲染回执
└── qc/                       抽检帧
第二集/  第三集/              待制作
```

成片 `01-序言-面向工科的拓扑学.mp4`（9.9 MB）随仓库提供；分段画面 `renders/`、旁白中间素材与字体未入库，按下面命令与来源重建。

## 复现

依赖：Manim Community 0.19.x、FFmpeg 4.4+、TeX Live（standalone / amsmath / mathrsfs / preview / xeCJK / ctex）、Python 3.12+。

```bash
cd 第一集

python3 scripts/fetch_voice.py        # 从 voice-urls.json 取回 48 句配音
python3 scripts/make_timing.py        # 按配音实测时长重排时间表
python3 scripts/render_all.py         # 渲染 10 段（也可只写 s2 s10）
python3 scripts/make_composition.py   # 生成 composition.json
# 合成：compose_media.py register-audio / check / render
```

两个必须知道的坑：

1. `MathTex` 用自定义 `TexTemplate` 注入 `\usepackage{mathrsfs}`，否则 `\mathscr{C}` 报 Undefined control sequence。
2. 中文统一 `Text(font="Noto Sans CJK SC")`，需要 xelatex + xeCJK + ctex。

配音细节：句子 31/32/40/41 的 `x₁ / x₂ / x₃ / xₙ` 在 `script.json` 的 `voice_text` 里改读为「X 一 / X 二 / X 三 / X N」，字幕保留原写法。

## 版本

- `v1.0` — 第一集完成：10 段画面、48 句旁白、48 条字幕、成片过合成预检（deliveryReady = true）

## 许可

代码与讲稿采用 [MIT](LICENSE)。字体 Noto Sans SC 依 [SIL Open Font License 1.1](https://fonts.google.com/noto/specimen/Noto+Sans+SC) 分发，放到 `第一集/fonts/` 即可复现字幕样式。
