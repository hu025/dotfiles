---
name: hyperframes
description: HeyGen HyperFrames — HTML-first video rendering pipeline for AI agents (Apache 2.0, 2026-04)
triggers:
  - hyperframes
  - HTML video rendering
  - AI agent video production
  - 视频自动化
updated: 2026-09-27
---

# HyperFrames — HTML → MP4 Video Rendering Framework

## 核心定位

**Write HTML. Render video. Built for agents.**

HyperFrames 是 HeyGen 开源的 Apache 2.0 框架（2026-04 发布），将 HTML/CSS/动画渲染为 deterministic MP4。核心差异化：AI coding agent 原生支持，skills 系统让任何 agent 一句话生成视频。

## 核心能力

### 引擎原理：Seek-Based Deterministic Rendering
1. **Compose**：用标准 web 技术写 HTML composition
2. **Preview**：`npx hyperframes preview` 启动 Hyperframes Studio，HMR 热更新
3. **Render**：headless Chrome seeks to each frame（`frame = floor(time * fps)`）→ FFmpeg encode

```
HTML element          → video clip
data-* attributes     → timeline controls
GSAP/Lottie/CSS       → seekable animation
Headless Chrome       → frame capture
FFmpeg                → MP4 encode
```

### 关键特性

- **Deterministic**（确定性）：相同输入永远产生相同像素输出，CI 友好
- **Agent-native**：skills 系统让 Claude Code / Cursor / Codex / Gemini CLI 直接使用
- **seekable animation**：GSAP timelines 必须 `{ paused: true }` 并注册 `window.__timelines`
- **multi-runtime adapters**：GSAP / Lottie / Three.js / Anime.js / CSS / WAAPI / TypeGPU
- **AWS Lambda rendering**：分布式渲染支持

### Composition 基础规则（Rule of Three）

1. **Root element**：必须有 `data-composition-id`、`data-width`、`data-height`
2. **Timed elements**：必须有 `class="clip"`、`data-start`、`data-duration`、`data-track-index`
3. **Animations**：GSAP timelines 必须 `{ paused: true }`，注册 `window.__timelines`

```html
<div id="root" data-composition-id="demo" data-width="1920" data-height="1080">
  <video id="clip-1" data-start="0" data-duration="5"
         src="intro.mp4" data-track-index="0" muted></video>
  <h1 id="title" class="clip" data-start="1" data-duration="4"
      data-track-index="1" style="font-size: 72px; color: white;">
    Welcome to Hyperframes
  </h1>
  <audio id="bg-music" data-start="0" data-duration="5"
         data-track-index="2" data-volume="0.5" src="music.wav"></audio>
</div>
```

### 20 Skills 系统（Router + Creation Workflows + Domain Skills）

| Skill | 用途 |
|---|---|
| `/hyperframes` | **Router** — 能力地图，所有请求的入口，选择 creation workflow |
| `/product-launch-video` | 网站/产品发布视频（up to ~3min） |
| `/faceless-explainer` | 纯文本概念解释（无产品/URL，每帧 LLM 生成） |
| `/pr-to-video` | GitHub PR → changelog / feature-reveal 视频 |
| `/embedded-captions` | 现有视频添加字幕 |
| `/talking-head-recut` | 采访视频 + 设计图形叠加 |
| `/motion-graphics` | 无旁白 motion graphic（< 10s） |
| `/music-to-video` | 音乐 → beat-synced 视频 |
| `/slideshow` | 演示文稿/幻灯片（Deck，非视频） |
| `/general-video` | 其他所有场景的 fallback |
| `/hyperframes-core` | Composition 契约：data-* timing、class="clip"、tracks |
| `/hyperframes-animation` | 所有动画知识：motion rules、scene blueprints |
| `/hyperframes-keyframes` | Seek-safe keyframe 跨 runtime 创作 |
| `/hyperframes-creative` | 非动画创意方向：frame.md / design.md |
| `/media-use` | 媒体 OS：BGM/SFX/图片/TTS 生成/转录 |

## 安装与使用

```bash
# 安装 skills（推荐）
npx skills add heygen-com/hyperframes
# 或从 main 直接安装最新
npx hyperframes skills update

# 初始化项目
npx hyperframes init my-project --example swiss-grid

# 预览（浏览器 Studio + HMR）
npx hyperframes preview

# 渲染草稿
npx hyperframes render --quality draft

# 渲染交付
npx hyperframes render --quality high --output final.mp4
```

## 包结构

| Package | 功能 |
|---|---|
| `hyperframes` (CLI) | 创建/preview/lint/render compositions |
| `@hyperframes/core` | Types、parsers、generators、linter、runtime |
| `@hyperframes/engine` | Seekable page-to-video capture（Puppeteer + FFmpeg） |
| `@hyperframes/producer` | 完整渲染管线：capture + encode + audio mix |
| `@hyperframes/studio` | 浏览器 composition editor UI |
| `@hyperframes/player` | `<hyperframes-player>` web component |
| `@hyperframes/shader-transitions` | WebGL shader transitions |
| `@hyperframes/aws-lambda` | AWS Lambda 分布式渲染 |

## 与 Hermes 相关性

### 潜在集成场景

1. **ETF 报告视频化**：结合 china-etf-technical-analysis skill，生成 K 线解读视频
2. **小说推广视频**：将小说章节内容生成为配乐视频短片
3. **早报可视化**：将行业早报内容自动渲染为视频

### 不适用场景

- 不生成 AI avatar（是 HeyGen 独立产品）
- 不做视频编辑（是渲染引擎）
- 不支持实时协作

## 技术限制

- **Node.js 22+** 必需
- **FFmpeg** 必需
- Git LFS 用于 golden test baselines（240MB .mp4）
- Chrome headless rendering 资源消耗较高

## 来源

- https://github.com/heygen-com/hyperframes
- https://hyperframes.heygen.com/introduction
- https://blog.nidhin.dev/video-as-code-a-deep-dive-into-heygen-s-hyperframes
