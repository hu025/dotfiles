# 行业新闻来源速查

## 无人机行业推荐来源

### 新闻聚合搜索（首选）
| 来源 | URL | 特点 |
|------|-----|------|
| 网易新闻搜索 | `https://www.163.com/search?keyword=无人机` | 速度快，标题摘要丰富，网易号标注来源。**实测可用，browser 工具唯一可靠方式** |
| 百度新闻 | `https://www.baidu.com/s?wd=无人机+新闻` | 新闻源广，含百家号内容（未实测） |

### 行业垂直媒体（browser 访问）
| 来源 | 备注 |
|------|------|
| 环球网 (`tech.huanqiu.com`) | 无人机相关新闻较多 |
| uav1.com | 无人机行业垂直门户，实测可访问（55万字节），但内容通过 JavaScript 渲染 |

### 英文来源（备选）
| 来源 | URL | 状态 |
|------|-----|------|
| Ars Technica RSS | `https://feeds.arstechnica.com/arstechnica/index` | ✅ 实测可用，有无人机/机器人相关文章 |
| HackerNews UAV 搜索 | `https://hnrss.org/newest?q=uav` | ✅ 可用但内容较旧（多为开源/学术项目） |
| The Verge RSS | `https://www.theverge.com/rss/index.xml` | ⚠️ 可用但无近期无人机内容 |

### 已验证不可用（不要使用）
| 来源 | 问题 |
|------|------|
| Google News RSS | 返回 0 字节，被屏蔽 |
| Bing News 中文 | 返回约 200 字节重定向页，bot 检测 |
| Sogou 新闻 | 返回约 150 字节，bot 检测 |
| 百度新闻搜索 | 返回约 150 字节，bot 检测 |
| 新浪 RSS/tech.sina.com.cn | JavaScript 渲染，内容不可提取 |
| 知乎话题页 | 返回约 650 字节，内容不可提取 |

## 工作流程关键节点

1. 导航到 `https://www.163.com/search?keyword={行业关键词}` → browser_navigate
2. 加载 compact snapshot，提取 heading 元素（@e3 等 ref 编号）的标题文本
3. 标题下方相邻的 StaticText 为来源和日期，标题链接的 href 为文章 URL
4. 筛选当天/前一天、5条以上高质量新闻
5. 如需深度内容，点击进入详情页，snapshot(full=true)
6. 编译为 Markdown 输出，每条 80 字以内，3-5 条，总字数不超过 500

## 已知问题与规避

- **中文新闻站 curl/terminal 直接请求全部失败** — 因 JavaScript 渲染或 bot 检测，返回 0-200 字节无效内容。必须用 browser 工具。
- **Google News RSS / 任何中文 RSS 均不可用** — 所有测试返回 0 字节。
- **英文 RSS 是唯一可用的 RSS 途径** — Ars Technica 最稳定，HackerNews 次之。
- **搜索延迟**：早上任务运行时当天新闻可能未收录，多用前一天的新闻。
- **军事新闻干扰**：俄乌冲突等新闻会混入，排除标准：与行业技术/商业无关。
- **战乱地区新闻**：俄乌/中东等地区的无人机新闻多为军事战报，与行业技术动态无关时应排除。
