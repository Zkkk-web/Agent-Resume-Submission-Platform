# JD 定制材料契约

定制过程使用 `.fanhan-job-agent/tailored-proposal.json`。先生成带变更依据的 Markdown 审核稿，再生成 `.fanhan-job-agent/outbox/` 下可编辑、可打印为 PDF 的 HTML；原始简历永远只读。

```json
{
  "schema_version": "fanhan-tailored-material-v1",
  "job": {
    "id": "工作台岗位 ID 或外部岗位稳定链接",
    "company": "目标公司",
    "title": "岗位名称"
  },
  "artifact_stem": "候选人姓名-目标公司-目标岗位-YYYYMMDD-v1",
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

## 完整性与文件名

- `sections` 必须构成一份完整可投递简历，不能只包含零散修改建议。
- 修改建议先在聊天中向候选人展示，再进入成稿。
- `artifact_stem` 必须由职业档案中的候选人姓名和当前岗位的公司、职位生成，格式为 `姓名-目标公司-目标岗位-YYYYMMDD-vN`。
- 原简历文件名中的公司不能继承到新版本，除非它就是当前目标公司。
- HTML 页面右上角提供“导出 PDF”；用户检查或编辑后，按同一 `artifact_stem` 保存 PDF。

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
