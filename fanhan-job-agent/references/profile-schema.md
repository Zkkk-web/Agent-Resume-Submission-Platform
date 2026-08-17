# 本地职业档案契约

文件位置：当前工作区 `.fanhan-job-agent/profile.json`。原始材料不进入该 JSON，只保存路径、结构化事实和证据位置。

```json
{
  "schema_version": "fanhan-career-profile-v1",
  "resume": {
    "path": "/path/to/resume.pdf",
    "sha256": "unknown"
  },
  "contact": {
    "email": "unknown",
    "phone_or_wechat": "unknown"
  },
  "intent": {
    "target_roles": [],
    "employment_type": "unknown",
    "preferred_locations": [],
    "remote_preference": "unknown",
    "relocation_preference": "unknown",
    "available_from": "unknown",
    "work_authorization": "unknown",
    "salary_expectation": "unknown",
    "target_industries": [],
    "company_preferences": []
  },
  "education": {
    "status": "unknown",
    "items": []
  },
  "core_experiences": {
    "status": "unknown",
    "items": []
  },
  "optional_links": [],
  "evidence": {},
  "consent": {
    "confirmed": false,
    "confirmed_at": "unknown",
    "material_version": "unknown",
    "idempotency_key": "unknown"
  }
}
```

## 枚举

- `employment_type`：`internship`、`full_time`、`either`、`unknown`
- `remote_preference`：`accept`、`reject`、`conditional`、`unknown`
- `relocation_preference`：`accept`、`reject`、`conditional`、`unknown`
- `work_authorization`：`unknown`，或候选人明确拥有的工作许可字符串数组。
- `education.status` / `core_experiences.status`：`known` 或 `unknown`。明确确认“没有”也属于 `known`，`items` 可以为空。

## 证据

每个非未知的可匹配字段都要在 `evidence` 中留下至少一条来源说明。键使用字段路径，例如：

```json
{
  "evidence": {
    "contact.email": ["resume.pdf 第 1 页"],
    "intent.preferred_locations": ["候选人于本轮明确回答：上海、杭州"],
    "education": ["resume.pdf 教育经历"],
    "core_experiences": ["resume.pdf 项目经历"]
  }
}
```

只记录来源位置或候选人确认，不复制大段简历正文。当前城市不是期望地点证据；模型推断不是远程或搬迁意愿证据。

## 两种状态彼此独立

- `profile_status=待补充/可匹配`：只表示材料是否足以进入岗位推荐。
- `ingest_ready=true/false`：只表示是否具备原始简历、有效联系方式和可审计授权。

因此，“待补充但已授权”的候选人可以入库，不能进入岗位推荐；“可匹配但未授权”的候选人只能留在本地，不能上传泛函。
