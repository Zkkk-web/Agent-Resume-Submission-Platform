---
name: apply-external-jobs
description: 旧版外部岗位执行入口。仅当用户明确使用 $apply-external-jobs 时触发，并立即转交 $genius-career-advisor-fanhan。新用户不需要单独安装或调用本 Skill。
---

# 外部岗位旧入口

这是兼容旧 Prompt 的别名，不是独立产品入口。

1. 告诉用户：现在统一使用 `$genius-career-advisor-fanhan`，原请求不会丢失。
2. 转交 `$genius-career-advisor-fanhan`；外部岗位由其内置 `internal/external-jobs/` 模块执行。
3. 不复制另一套建档、找岗、选岗、隐私确认、提交或日志逻辑。
