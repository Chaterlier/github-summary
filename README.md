# GitHub Issue 日报助手

每天自动抓取指定 GitHub 仓库过去 24 小时的 issue 动态，由 AI 撰写带分层总结的中文日报并邮件推送。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `repos.txt` | 监控仓库列表，每行一个 `owner/repo`，`#` 开头为注释 |
| `fetch_issues.py` | 抓取各仓库过去 24 小时的 issue 动态，输出 JSON 并保存 `digest_YYYY-MM-DD.json` |
| `send_email.py` | 读取日报 Markdown，渲染为 HTML 后经 SMTP 发送邮件 |
| `mail_config.json` | 邮箱配置（含授权码，**已 gitignore，不入库**），参考 `mail_config.example.json` |

## 使用方法

```bash
# 1. 抓取 issue 动态（可选：设置 GITHUB_TOKEN 环境变量提高 API 限流额度）
python fetch_issues.py

# 2. 基于 digest JSON 撰写日报 report_YYYY-MM-DD.md（当前由 AI 助手完成）

# 3. 发送邮件
python send_email.py report_YYYY-MM-DD.md
```

## 日报结构约定

- 标题：`GitHub Issue 日报（日期）`
- **今日总结**：按项目分别汇总，每个项目一段话提炼核心要点、严重程度与趋势判断
- **每个仓库一节**：
  - 概览 = 数据（open 总数 / 新增 / 更新 / 关闭）+ 一句总结性语句概括当日动态特征
  - 新增和有实质更新的 issue 各用 1-2 句话概括内容、影响面与意义，附编号和链接
  - 评论数多的活跃讨论重点说明；关闭的 issue 简单列出编号标题
  - 末尾「本仓库小结」：按主题聚类当日 issue，提炼共性问题
- 末尾注明数据获取时间

## 当前监控仓库

- [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling)
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- [typesafe-ai/skills](https://github.com/typesafe-ai/skills)

新增监控：直接在 `repos.txt` 追加一行即可。

## 定时任务

由 Kimi Work 定时任务驱动：每天 09:00（Asia/Shanghai）自动执行抓取 → 撰写 → 发送全流程。

## 依赖

- Python 3.10+，仅标准库即可运行抓取
- 发送邮件时优先使用 `markdown-it-py` 渲染 HTML（未安装时自动降级为纯文本包裹）
