# Skills 配置和使用指南

## 📖 什么是 Skills？

Skills 是 Lingma AI 助手的技能配置文件，用于教导 AI 如何执行特定任务。每个 Skill 是一个 Markdown 文件，包含详细的操作指南和最佳实践。

## 🎯 如何创建 Skills

### 方法一：使用 create-skill 工具（推荐）

在对话中使用：
```
/create-skill
```

然后按照提示创建新的 Skill。

### 方法二：手动创建

1. 在项目根目录创建 `.lingma/skills/` 目录
2. 创建 `.md` 格式的 Skill 文件
3. 按照标准格式编写内容

## 📝 Skill 文件格式

```markdown
---
name: skill-name
description: 简短描述这个技能的用途
version: 1.0.0
---

# Skill 名称

## 何时使用

说明在什么场景下应该使用这个技能。

## 执行步骤

1. 第一步做什么
2. 第二步做什么
3. ...

## 示例

提供具体的使用示例。

## 注意事项

- 需要注意的点
- 常见的错误
```

## 🔧 当前项目可用的 Skills

查看 `skills-main/` 目录了解已安装的 skills。

## 💡 项目管理 Skills 示例

让我为您创建一个项目管理相关的 Skill：
