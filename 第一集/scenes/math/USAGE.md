# Manim Community Edition backend

这是独立的 Manim CE 0.19.0 项目，不经过 Remotion。默认 `SmokeScene`
为 1920×1080、24 fps、48 帧（2 秒）的内部无声几何演示，不是用户视频的内容模板。
按任务编辑 `scene.py`，在 `video-config.json` 统一指定画布与总帧数。

缺省正式输出要求原生渲染短边至少 1080 像素，入口会把配置尺寸显式传给 Manim，
并验证实际输出尺寸。低清试帧须在独立预览工程中设置 `render-profile.json` 为
`{"mode":"preview"}`，回执 `deliveryReady:false`；不能覆盖已有正式或未标记的旧视频。
用户明确要求其他尺寸时用 `{"mode":"custom","reason":"用户要求的具体尺寸"}`。
禁止把低清 Manim 片段后期拉伸成正式高清输出。

## 仅安装本路线所需依赖

推荐在 Python 3.11/3.12 的独立虚拟环境运行：

```sh
python -m pip install -r requirements.txt
python scripts/render.py
```

这里固定的是 **Manim Community Edition**，不是 ManimGL。系统需有可执行的
`ffprobe`（通常随 FFmpeg 安装）。Cairo/Pango、编译器等原生构建依赖是否需要
额外安装取决于操作系统与可用 wheel；安装失败时按 CE 对应平台说明补齐，runner
不会自动安装 Python 包、系统工具或其他后端。Manim CE 自身的编码由其依赖管理。
Manim CE 的 Cairo 路线还需要可用的 Cairo/Pango 与 Python 绑定；pip 没有适合目标平台的
wheel 时需按该平台准备开发库和构建工具。仅在选中 Manim 时准备这些依赖，不要求其他
路线安装它们。默认场景不使用 Text/MathTex/Tex，所以不需要 LaTeX或额外字体；新增文字时可注册
初始化器复制的 `public/fonts/NotoSansSC-Regular.otf`，保留其 `OFL.txt`。

`PYTHON` 可指定供 `-m manim` 使用的 Python 可执行文件；默认使用运行 runner 的
`sys.executable`。`FFPROBE_PATH` 可指定 ffprobe 可执行文件。二者为单个可执行路径，
不接受拼接 shell 参数。选择别的场景类：`python scripts/render.py --scene=MyScene`。

## 输出与验证契约

- `out/video.mp4`：本次新渲染的完整文件。
- `out/render-result.json`：计划规格与 ffprobe 实测宽高、帧率、解码帧数、时长、音轨数。
- 使用 `ffprobe -count_frames`，宽高/帧率/帧数必须与配置相符才发布视频。未取得实测
  数据或缺工具会失败，不把配置值冒充实测值。
- `metadataVerified` 只表示媒体技术规格检查通过，不代表内容、排版、旁白或视听质量验收。

此渲染入口只输出画面素材；整片按用途加入已经取得并核验的声音。数学讲解固定使用包内豆包参考旁白，纯视觉展示默认自主配节奏音乐；使用Manim本身不决定声音类型。
场景的所有 play/wait 总时长应匹配 `frames/fps`；修改动画后由实际帧数检查捕获偏差。
源文件、配置和依赖声明均可编辑；不随模板存放虚拟环境、缓存或二进制渲染产物。
