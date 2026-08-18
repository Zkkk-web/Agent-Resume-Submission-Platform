---
name: apply-external-jobs
description: 从 Bonjour、Watcha 和 JobRadar 探索岗位，并在 Codex 内置浏览器中完成选岗确认、表单辅助和最小结果记录。适用于泛函求职 Agent 的外部招聘网站流程；Bonjour、Watcha 可作为直接申请候选，JobRadar 受登录/会员限制。不得切换系统默认浏览器、绕过验证码、付费限制、猜测申请事实或替用户点击最终提交。
---

# 外部招聘平台辅助投递

这是 `$fanhan-job-agent` 的内部执行 Skill，不是另一个产品入口。开始前读取 [V1 contract](references/v1-contract.md)；执行验收时再读取 [test record template](references/test-record-template.md)。

## 对话风格

- 默认像微信对话：先说结论，通常 1–3 个短句，每轮只推进一个问题或动作。
- 不复述长背景；需要用户接管时，只说当前卡点、要做的动作和完成后如何继续。
- 个人数据发送范围、失败状态和最终提交摘要必须完整，不得为了简短而省略。

## 工作流

1. 返回 `$fanhan-job-agent`，确认 `$职业资产` 已生成非空 `.fanhan-job-agent/职业经历.md`、`.fanhan-job-agent/profile.json` 和与当前档案哈希一致的 `profile-status.json`。状态不是 `可匹配` 时停止找岗并补齐最小缺口；不得用原始简历直接开始搜索。
2. 使用 `scripts/application_log.py duplicate` 检查工作区 `.fanhan-job-agent/external-applications.jsonl`；命中成功记录时跳过，除非用户明确要求重投。
3. 优先运行 `python3 <skill-root>/scripts/external_jobs.py --query '<求职关键词>' --limit 20`，一次读取 Bonjour、Watcha 和 JobRadar 的结构化状态。岗位发现不得依赖浏览器渲染；单一来源失败不得阻塞其他来源。Bonjour、Watcha 可作为站内申请候选；JobRadar 未获得合作 API 前必须如实标记免费预览或会员限制，不得绕过。不得调用系统默认浏览器。
4. 展示来源、公司、职位、地点、岗位链接、申请链接、匹配点、缺口和风险。当前打开页面只算环境上下文，绝不等于用户选择。
5. 用户明确选择单个岗位后，运行 `scripts/confirmation_gate.py select`，把公司、职位、岗位链接、申请链接和选择时间写入 `.fanhan-job-agent/selected-external-job.json`。记录缺失或与当前岗位不一致时，禁止发送个人数据、上传材料或准备提交。
6. 返回 `$fanhan-job-agent` 执行“选岗后的统一定制流程”：展示匹配点、缺口、风险和具体修改建议；生成与当前公司和职位绑定的完整 HTML 简历；由用户检查并导出同名 PDF。缺少任一产物时不得打开申请表。
7. 登录、扫码和验证码由用户接管。输入个人信息或上传文件前，运行 `confirmation_gate.py build`；脚本会校验职业主档、档案状态、岗位提案和当前岗位专用 PDF。失败时不得绕过。
8. 能可靠预填的文字字段尽量填写；不能可靠填写时，按字段给出可直接复制的短答案。文件选择器不稳定时，只给出门禁通过的岗位专用 PDF 链接，请用户拖到右侧申请页。
9. 展示最终摘要，并在交给用户点击前用与 `build` 完全相同的公司、岗位、档案、材料和字段参数运行 `scripts/confirmation_gate.py verify`，再附加 `--expected '<build 返回的 fingerprint>'`。选岗、页面、材料或字段变化时必须停止。V1 最终提交按钮由用户本人点击。
10. 用户点击后，只凭明确成功文案、申请编号或平台状态记录 `success`；明确失败记为 `failed`；结果含糊或超时记为 `failed: submission_outcome_unknown`，不得自动重试。

## 外部来源读取规则

1. Bonjour 从公开职位页随页面返回的岗位数据读取；不要先打开右侧栏逐卡滚动。脚本没有识别到岗位时标记 `暂不可用`，不得写成 `无结果`。
2. Watcha 从查岗页自己使用的公开接口 `https://watcha.cn/jobs-api/v1/public/teams` 读取。`/study/jobs` 是 SPA 路由，初始标题或营销文案不能作为“没有岗位”的证据。
3. JobRadar 默认返回 `membership_required`：免费层只提供基础预览，完整岗位与投递入口需登录/会员。未获得合作 API 前不得直接读取其后台数据库绕过限制。
4. 右侧栏浏览器只在用户选中岗位后用于查看详情、登录和申请。公开数据读取失败时保留结构化失败状态并继续其他来源，不用浏览器反复重试搜索。

## 硬边界

- 不绕过验证码，不保存密码、Cookie、Token 或登录态。
- 日志不保存简历正文、作品集正文、表单答案、证件信息或联系方式。
- 原始简历和仅做格式转换的 PDF 不得上传；文件名未绑定当前候选人、公司和职位时不得进入申请页。
- V1 只做辅助投递；托管代投留到具体网站适配稳定并另行定义授权后。
- 不因用户曾说“都投”或“继续”而跳过当前岗位确认。
- V1 外部来源只覆盖 Bonjour、Watcha 和 JobRadar；不同真实申请站点不承诺稳定适配。
- V1 不支持 WorkBuddy 外部投递、云端账号/数据库、积分付费或自动批量代投。

## 常用命令

```bash
python3 scripts/confirmation_gate.py select --company '<公司>' --job-title '<职位>' --job-url '<岗位链接>' --application-url '<申请链接>' --output .fanhan-job-agent/selected-external-job.json --confirmed
python3 scripts/external_jobs.py --query '<求职关键词>' --limit 20
python3 scripts/watcha_jobs.py --query '<求职关键词>' --limit 20
python3 scripts/application_log.py duplicate --job-url '<岗位链接>' --application-url '<申请链接>'
python3 scripts/confirmation_gate.py build --company '<公司>' --job-title '<职位>' --job-url '<岗位链接>' --application-url '<申请链接>' --profile .fanhan-job-agent/profile.json --profile-status .fanhan-job-agent/profile-status.json --career-document .fanhan-job-agent/职业经历.md --proposal .fanhan-job-agent/tailored-proposal.json --resume '.fanhan-job-agent/outbox/<姓名-目标公司-目标岗位-日期-vN.pdf>' --field-name email --field-name phone --final-action '<按钮文字>' --selection .fanhan-job-agent/selected-external-job.json
python3 scripts/confirmation_gate.py verify --company '<公司>' --job-title '<职位>' --job-url '<岗位链接>' --application-url '<申请链接>' --profile .fanhan-job-agent/profile.json --profile-status .fanhan-job-agent/profile-status.json --career-document .fanhan-job-agent/职业经历.md --proposal .fanhan-job-agent/tailored-proposal.json --resume '.fanhan-job-agent/outbox/<姓名-目标公司-目标岗位-日期-vN.pdf>' --field-name email --field-name phone --final-action '<按钮文字>' --selection .fanhan-job-agent/selected-external-job.json --expected '<build 返回的 fingerprint>'
python3 scripts/application_log.py append --source '<Bonjour|Watcha|JobRadar>' --company '<公司>' --job-title '<职位>' --job-url '<岗位链接>' --application-url '<申请链接>' --status user_declined --user-confirmed false --reason user_declined
```
