# JD 定制材料契约

定制过程使用 `.fanhan-job-agent/tailored-proposal.json`，最终成稿必须写为 `.fanhan-job-agent/` 下的新 Markdown 文件。原始简历永远只读。

```json
{
  "schema_version": "fanhan-tailored-material-v1",
  "job": {
    "id": "工作台真实岗位 ID",
    "title": "岗位名称"
  },
  "sections": [
    {
      "heading": "相关经历",
      "content": "定制后的正文",
      "change_ids": ["change-1"]
    }
  ],
  "changes": [
    {
      "id": "change-1",
      "type": "rewrite",
      "summary": "把已有经历改写为岗位相关表达",
      "jd_basis": ["JD 中的具体要求或位置"],
      "fact_evidence": ["简历中的证据位置或候选人明确回答"],
      "confirmation": "not_required"
    }
  ]
}
```

## 变更类型

- `reorder`：只调整已有内容顺序，不改变事实；`confirmation=not_required`。
- `rewrite`：只改写已有事实，不新增数字、职责、技能、时间或成果；`confirmation=not_required`。
- `fact_addition`：加入原材料没有、但候选人补充的新事实；必须先逐项展示并取得确认。
- `fact_change`：改变原材料中的事实含义；必须先逐项展示并取得确认。

`fact_addition` 和 `fact_change` 只有在候选人明确确认后才能写为 `confirmation=confirmed`，同时记录 `confirmed_at`。拒绝、含糊答复和沉默均保持 `pending` 或从提案中删除，不能进入成稿。

## 依据规则

- 每项变更都必须同时有非空 `jd_basis` 和 `fact_evidence`。
- 每个成稿章节必须引用至少一个变更；每项变更也必须被成稿章节引用。
- 事实证据只写来源位置或候选人确认，不复制大段原始简历。
- 脚本只负责结构门禁，语义判断仍由 Agent 对照真实简历与 JD 完成；不确定时标为未知，不做润色推断。
