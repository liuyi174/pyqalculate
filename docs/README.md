# PyQalculate 项目文档

## 文档结构

```
docs/
├── plans/              # 开发计划（过程文档）
│   ├── DEVELOPMENT_PLAN_V1.md      # v1.0 开发计划
│   ├── DEVELOPMENT_PLAN_V2.md      # v2.0 开发计划
│   ├── DEVELOPMENT_PLAN_V2.1.md    # v2.1 开发计划
│   ├── DEVELOPMENT_PLAN_V2.1.1.md  # v2.1.1 开发计划
│   ├── DEVELOPMENT_PLAN_V2.1.2.md  # v2.1.2 开发计划
│   └── DEVELOPMENT_PLAN_V2.2.md    # v2.2 开发计划（当前）
│
├── standards/          # 编码规范（产品文档）
│   ├── PROJECT_STRUCTURE.md        # 项目结构
│   └── CODING_GUIDELINES.md        # 编码规范
│
├── analysis/           # 分析文档（产品文档）
│   ├── mainwindow.md               # 主窗口分析
│   ├── expression_edit.md          # 表达式输入分析
│   ├── result_view.md              # 结果显示分析
│   ├── history_view.md             # 历史记录分析
│   ├── keypad_analysis.md          # 键盘分析
│   ├── conversionview_analysis.md  # 单位转换分析
│   ├── menu_dialog_system_analysis.md  # 菜单对话框分析
│   ├── buttonseditdialog_analysis.md   # 按钮编辑分析
│   ├── overview.md                 # 架构概览
│   └── README.md                   # 分析文档索引
│
└── README.md           # 本文件
```

## 文档分类

### 过程文档（Process Documentation）

描述开发过程，记录计划、决策和进展。

- **开发计划**: 每个版本的开发目标、任务分解、时间安排
- **会议记录**: 重要的技术讨论和决策
- **变更日志**: 版本发布说明

### 产品文档（Product Documentation）

描述系统本身，提供技术参考。

- **项目结构**: 目录组织、模块职责、依赖关系
- **编码规范**: 代码风格、命名规则、最佳实践
- **API 文档**: 公共接口说明
- **分析文档**: 原项目架构分析、设计决策

## 文档维护

### 更新频率

- **过程文档**: 每个版本更新
- **产品文档**: 重大变更时更新
- **编码规范**: 定期审查（每季度）

### 审查流程

1. 代码变更时同步更新文档
2. Pull Request 包含文档更新
3. 重大变更需要文档审查

### 归档策略

- 过时的计划文档保留在 `plans/` 目录
- 过时的规范文档移至 `archive/` 目录
- 删除前需要团队确认

## 相关资源

- [项目 README](../README.md)
- [GitHub 仓库](https://github.com/anotlife/pyqalculate)
- [问题追踪](https://github.com/anotlife/pyqalculate/issues)

---

*最后更新: 2026-06-21*
