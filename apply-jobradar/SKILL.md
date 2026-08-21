---
name: apply-jobradar
description: 旧版 JobRadar Skill 名称的兼容入口。仅当用户明确使用 $apply-jobradar 或要求从 JobRadar 找岗位时触发；立即转交 $genius-career-advisor-fanhan。不得维护独立投递逻辑。
---

# JobRadar 旧入口

这是兼容旧 Prompt 的别名，不是独立产品入口。

1. 告诉用户：现在统一使用 `$genius-career-advisor-fanhan`，原请求不会丢失。
2. 调用 `$genius-career-advisor-fanhan` 整理真实材料和偏好；外部岗位步骤使用其内置模块。
3. JobRadar 只作岗位发现源；实际申请遵循来源站点流程。
4. 不复制另一套选岗、隐私确认、提交或日志逻辑。
