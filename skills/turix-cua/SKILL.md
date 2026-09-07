---
name: turix-cua
description: TuriX桌面级Computer-Use Agent：AI控制桌面GUI（macOS/Win/Linux），OSWorld 64.2%，macOS 80%+，支持OpenClaw skill集成
---

# TuriX-CUA 桌面Computer-Use Agent

## 核心数据
- **GitHub**: github.com/TurixAI/TuriX-CUA
- **stars**: 3K+
- **License**: MIT
- **分支**: main(macOS) / multi-agent-windows / multi-agent-linux

## 核心定位
AI agents控制桌面GUI——点击、输入、导航，跨浏览器/办公套件/消息应用，覆盖一切人可操作的界面。
vs browser-use：browser-use专注浏览器内，TuriX-CUA覆盖整个桌面OS。

## 架构
- **VLM Brain**: 感知屏幕内容
- **Actor Model**: 执行GUI动作
- **Planner**: 规划任务步骤
- **Memory**: 可恢复内存压缩（中断后可续接）
- **Skills**: markdown playbook格式，任务规划用
- **config.json**: 单文件配置所有模型参数

## 性能
- OSWorld Benchmark: 64.2%（第3名）
- macOS自测: 80%+成功率
- 支持50步长任务

## 2026更新
- TuriX SuperAgent桌面App发布（2026-05-11）
- TuriX 3.0.0-alpha: CUA+CLI合一，TuriX-work(办公编排)+TuriX-code(编码自动化)
- Linux分支上线（multi-agent-linux）
- Recoverable Memory Compression（中断可续接）
- OpenClaw skill集成（ClawHub: clawhub.ai/Tongyu-Yan/turix-cua）

## 安装（macOS Apple Silicon）
```bash
git clone -b main https://github.com/TurixAI/TuriX-CUA.git
cd TuriX-CUA
conda create -n turix python=3.12
conda activate turix
pip install -e .
# macOS: 系统偏好设置 → 隐私与安全 → 辅助功能 → 允许Turix
# Safari: 开发 → 允许远程自动化
```

## 配置文件
config.json可自定义：VLM模型、Actor模型、平台参数

## OpenClaw集成
```bash
# ClawHub安装
clawd skill install https://clawhub.ai/Tongyu-Yan/turix-cua

# 本地skill（macOS）
cp -r OpenCLaw_TuriX_skill/ ~/.clawd/skills/local/turix-mac/
```

## 适用场景
- 桌面应用自动化（非浏览器）
- 跨应用工作流（邮件+文档+表格联动）
- macOS原生应用控制
- 需要桌面级操作而非仅浏览器的任务

## 局限性
- 专注macOS优化，Windows/Linux较新
- 配置相对复杂（conda+权限）
- stars少（3K），社区规模小
