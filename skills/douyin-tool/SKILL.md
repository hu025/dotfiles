---
name: douyin-tool
description: Use when reading Douyin (TikTok China) video comments, fetching video metadata/stats, listing the recommend feed, or preparing a post. Uses CloakBrowser stealth Chromium to bypass the captcha interstitial and calls Douyin's own web APIs from inside the page context (x-bogus signing handled by the page). Trigger on 抖音/douyin/读评论/视频数据/推荐流/发布图文.
---

# 抖音工具（评论读取 / 视频信息 / 推荐流）

不依赖 SnowLuma、DeepSeek Harness 或抖音开放平台。用 **CloakBrowser 的 stealth Chromium**（已装 `146.0.7680.177`）+ Playwright，在页面上下文里 `fetch` 抖音自己的 web API —— 签名参数（x-bogus / a-bogus）由页面自己生成。

## 为什么需要 CloakBrowser

普通 chromium 访问 `douyin.com` 会落到「验证码中间页」（argus-csp-token），因为 `navigator.webdriver === true`。CloakBrowser 打补丁后 `navigator.webdriver === false`，能正常拿到推荐流、视频详情和评论。

本机已装：
- `~/.cloakbrowser/chromium-146.0.7680.177.5/chrome`
- `~/.agent-reach/tools/cloakbrowser/bin/python`（py3.13，自带编译好的 greenlet）

## 关键运行约束（踩过的坑）

**必须用 CloakBrowser 自带的 venv python，且清掉 PYTHONPATH：**

```sh
env -u PYTHONPATH ~/.agent-reach/tools/cloakbrowser/bin/python douyin_tool.py ...
```

原因：Hermes 的 `PYTHONPATH` 里带着 py3.14 的 playwright，会串到 CloakBrowser 的 py3.13 venv，导致
`ModuleNotFoundError: No module named 'greenlet._greenlet'`（greenlet 的 C 扩展按 Python 版本编译，不通用）。

**必须用 `~/.hermes/douyin-profile` 作为 profile 目录**，不要每次新建 —— profile 里的 cookie（ttwid 等）是能过风控的必要条件之一。

## 用法

```sh
D=~/.hermes/skills/douyin-tool
P=~/.agent-reach/tools/cloakbrowser/bin/python

# 读评论
env -u PYTHONPATH $P $D/douyin_tool.py comments <aweme_id> --count 20

# 视频信息 + 统计数据
env -u PYTHONPATH $P $D/douyin_tool.py info <aweme_id>

# 推荐流
env -u PYTHONPATH $P $D/douyin_tool.py feed --limit 10

# 登录态检测
env -u PYTHONPATH $P $D/douyin_tool.py login-status

# 发布图文（需要登录态）
env -u PYTHONPATH $P $D/douyin_tool.py publish "文字内容" --images a.jpg
```

也可以直接当模块用：

```python
import sys
sys.path.insert(0, "/home/saber/.hermes/skills/douyin-tool")
from douyin_tool import fetch_comments, fetch_info, fetch_feed, login_status
```

## 返回格式

`comments`：

```json
{"ok": true, "aweme_id": "...", "total": 1006, "has_more": 1, "cursor": 10,
 "comments": [{"id": "...", "user": "昵称", "sec_uid": "MS4wLjAB...",
               "text": "评论内容", "digg": 904, "reply": 10,
               "create_time": 1786859800, "ip": "江苏"}]}
```

`info`：

```json
{"ok": true, "desc": "标题文案", "author": "作者", "create_time": 1786799469,
 "duration_ms": 1678060, "images": 0, "video": true,
 "stats": {"comment": 1006, "digg": 19609, "share": 1219, "collect": 2750}}
```

## 用到的接口

| 用途 | 接口 |
|---|---|
| 评论 | `GET https://www-hj.douyin.com/aweme/v1/web/comment/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=<id>&cursor=0&count=20&item_type=0` |
| 视频详情 | `GET .../aweme/v1/web/aweme/detail/?...&aweme_id=<id>` |
| 推荐流 | 页面 DOM 里带 19 位数字的 `data-item-id` / `data-aweme-id` / `href` |

所有请求都在 `page.evaluate()` 里发，`credentials: 'include'`，由页面注入正确的 UA / Referer。

## 已知限制

- **发布图文未完成**。`publish` 子命令目前只做到「定位到 creator 平台投稿页并判断登录态」，没有实现真正的图文上传与提交。抖音的发布按钮带风控二次校验，需要人在场确认。要做完整发布需要：① 登录态 ② 图文上传流程 ③ 手动过发布风控。
- **回复评论 / 发评论未实现**（同样需要登录态）。
- **登录态是空的，而且填不上**：`login-status` 显示 `logged_in: false`，几个 profile
  里都没有 `sessionid` cookie。这不是「还没做」，是登录域被风控（见下方
  「登录：不要再试这三条路」）。读评论、读详情不需要登录；写操作需要，而目前无解。
- 视频详情接口返回 140KB，`fetch_info` 只截取需要的字段。
- 每条命令都要起一次浏览器（约 15-30 秒），不适合高频轮询。

## 登录：不要再试这三条路

**抖音网页版的 passport 登录域对本机环境是风控的，三条路都不要花时间重试。**

- **扫码**：`passport/web/get_qrcode` 能拿到 token 并生成二维码图片，但
  `check_qrconnect` 轮询永远返回 `error_code=4031`「安全风险已阻止此次访问」。
  扫了也不会 confirmed。
- **登录框里的二维码根本不存在**：点开登录弹窗后，里面没有 `canvas`、没有
  `svg`、没有 qrcode 元素，只有一个 726×86 的背景图 —— 页面自己的
  `get_qrcode` 请求被同一个 4031 拦掉了，所以二维码压根没渲染。**别再往弹窗里
  找二维码。**
- **验证码**：手机号能填进去，但点「获取验证码」只触发一次
  `passport/user_info/get_sec_ts`（返回 `data:null`），**真正的短信请求不发出**，
  按钮不进倒计时也不报错。
- **账密**：切到「密码登录」tab 后 DOM 里**没有密码输入框**（仍是手机号+验证码），
  账密登录在网页版已废弃。直调 `passport/web/login/` 返回 `error_code=16`「该应用
  无权限」（缺 `device_platform` / `verifyFp` / `msToken` 签名参数）。

这是抖音服务端的决定，不是代码能改的。上游 `dsh-douyin-whale` 的做法就是
「服务器上扫码停在 qrcode 是预期行为，请在本地导出 cookie」——即本地有可见窗口的
浏览器手动登一次再导出 cookie，不追求自动化。

**读操作完全不需要登录**（评论、详情、推荐流都验证过能用），所以除非真的需要发
东西，不要碰登录。

## 页面交互技巧（验证过能用）

写 Playwright 脚本操作抖音时，下面这些是实测有效的写法：

- **点按钮用 `hover → mouse.down → mouse.up`**，JS `.click()` 不触发抖音的弹窗
  （登录弹窗就是这么开出来的）。
- **用 `page.fill()` 填输入框**。`keyboard.type()` 和 `insert_text()` 会被 stealth
  吞掉（值为空），`.focus()` 返回 False —— fill 走 CDP 通道所以能绕过。
- **按钮坐标每次都变**（同一个「登录」按钮观察到过 x=1212 和 x=1332），必须
  运行时定位，不要写死。定位时按「文本匹配 + 区域过滤（如 `r.top < 120`）+
  取最靠右」取最可能的那个。
- **视频卡片不是 `<a>` 标签**。从 `data-item-id` / `data-id` / `data-aweme-id` /
  `href` 属性里正则抓 19 位数字，再从最近的文案祖先元素拿标题和作者。
- **非 headless + Xvfb** 才有完整交互能力：`DISPLAY=:99`（本机 `Xvfb :99` 已在跑）。
  headless 下部分弹层不渲染。
- 评论接口在 **`www-hj.douyin.com`**（不是 `www.douyin.com`）。
- **签名不用自己实现**：在 `page.evaluate()` 里发 `fetch` 并带
  `credentials: 'include'`，x-bogus / a-bogus 由页面自己补上。
