# 夜来.skill

> 蒸馏自番茄小说金番作家**夜来风雨声丶**（《诡舍》《因为谨慎而过分凶狠》《天不应》作者）的全部长篇作品与本人访谈。
> 用途：写**灵异 / 悬疑惊悚小说**——单元诡计、规则怪谈、氛围恐怖、无限流长篇皆可。

基于 [Agent Skills](https://agentskills.io) 协议，可在 Claude Code / Codex / Cursor / OpenClaw / ZCode 等任何兼容 runtime 中使用。

## 安装

把本目录（`夜来-skill/`）复制到你所用 runtime 的 skills 目录即可，例如：

| Runtime | 路径 |
|---|---|
| Claude Code | `~/.claude/skills/夜来-skill/` |
| Codex CLI | `~/.codex/skills/夜来-skill/` |
| Cursor | `~/.cursor/skills/夜来-skill/` |
| OpenClaw | `~/.openclaw/workspace/skills/夜来-skill/` |

## 使用

装好后对 agent 说：

```
> 用夜来skill帮我构思一个新的灵异小说大纲
> 用夜来的风格写一个规则怪谈副本的开头
> 按夜来的方法给我这个恐怖单元设计规则和吓点
> 夜来skill：帮我审查这段恐怖描写，不够吓
```

典型触发词：「夜来」「写灵异小说」「规则怪谈」「诡舍风格」「恐怖副本」。

## 蒸馏来源

| 素材 | 规模 | 用途 |
|---|---|---|
| 《诡舍》全本 | 221万字 / 1017章（完结） | 主蒸馏对象：恐怖技法、单元结构、文风DNA |
| 《因为谨慎而过分凶狠》全本 | 214万字 / 875章（完结） | 三书对比：共性方法论、幽默配比 |
| 《天不应》 | 168万字（连载至2026-04） | 三书对比：紧张感技法的跨题材迁移 |
| 《诡舍2》 | 试读版（连载中） | 续作开篇参照 |
| 作者访谈×3（封面新闻/搜狐/凤凰网） | 一手自述 | 创作方法论：氛围恐怖论、情绪商品论、预演法 |

调研与分析过程见 `references/research/`（40 份蒸馏档案）；原始语料因版权不随库分发（`references/sources/` 需自备，见该目录说明）。

## 工具链

内置文风 / 情节双检查器（`scripts/`，纯 Python 无依赖）：

```
python scripts/check_chapter.py "validation/<书名>/第0*.md"        # 文风：拟声/标点/段落/对话占比 10 项
python scripts/check_plot.py   "validation/<书名>/第0*.md"        # 情节：章尾钩子/高潮章/结算章/死亡节拍/恐怖洼地 5 项
python scripts/repair_chapter.py / polish_chapter.py / analyze_style.py   # 修复 / 校样 / 统计
```

文件与目录命名规范见 `SKILL.md` §33。

## 许可

MIT License。本项目为非官方粉丝项目，与作者夜来风雨声丶无隶属关系；源作品版权归原作者及平台所有。

## 诚实边界

- 本skill提炼的是**写作方法论与文风规律**，不复制原文；生成内容为原创情节，但风格上近似夜来风雨声丶。
- 《诡舍》谜底级剧透仅用于内部规律提炼，不会在生成内容中原样复用其具体设定（血门/拼图等专有设定只作结构参照）。
- 风格近似≠本人水准；灵感与天才是蒸馏不出来的。

---

> 本Skill由 [女娲 · Skill造人术](https://github.com/alchaincyf/nuwa-skill) 方法论蒸馏生成
