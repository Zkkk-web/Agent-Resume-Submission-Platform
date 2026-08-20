# Agent Resume Submission Platform — V1

V1 对用户只有一个入口，内部依赖职业资产与外部网站安全骨架：

- `fanhan-job-agent`：调用 `$职业资产` 建立长期档案，默认同时搜索泛函、Bonjour、Watcha 和 JobRadar，统一去重和排序；选岗后生成岗位专用简历，并在候选人明确授权后辅助申请。
- `apply-external-jobs`：处理 Bonjour、Watcha 和 JobRadar 的岗位发现、选岗门禁、表单辅助与最小本地记录。
- `apply-jobradar`：仅兼容旧 Prompt，并转交上面两个 Skill，不维护独立逻辑。

V1 的外部网站模式是“辅助投递”：Agent 接受 PDF 或 DOCX，先建立职业档案；用户选岗后获得针对性建议和岗位专用简历。针对性提问结束后，第一份候选人可见成稿必须是绑定候选人、目标公司和岗位的可编辑 HTML，并立即在 Codex 侧边栏展示；页面在本地自动保存文字修改，并读取当前页面直接导出同名 A4 PDF，不依赖系统打印窗口。用户检查、修改并亲自导出后才能进入申请。Agent 先扫描完整申请表，可靠字段预填后重新读取复核；只要存在人工步骤，就一次性整理所有字段的值和状态供用户复制或上传。外部申请提交、失败或放弃后先取得泛函入库授权，核验工作台与飞书通知，再只提示可选面试辅助。托管代投不属于三天版。

申请表出现开放题时，主 Skill 会优先查找本地已确认回答，展示原公司和岗位后由候选人决定沿用、改写或重答；答案只保存在 `.fanhan-job-agent/candidate-memory.json`，不进入外部投递日志或工作台。候选人进入面试阶段后，可复用同一职业资产建立故事库、逐题模拟和复盘记录。当前不接入独立 Chrome、Playwright 或自动提交。

每个候选人目录另有两个互不混写的 Markdown：`用户求职记忆.md` 保存候选人确认的求职偏好，`Agent平台执行记忆.md` 保存招聘网站故障、解决办法和复用条件。`职业经历.md` 仍是职业事实主档，三者用途不同。

默认找岗不区分“先泛函、后外部”：用户没有限定来源时，同一轮必须尝试泛函工作台、Bonjour、Watcha 和 JobRadar，再统一展示。来源需要登录、会员或暂不可用时明确标记并继续其他来源，不能悄悄省略。

当前打开的招聘页面不代表用户选择。V1 在发送个人数据前必须先展示匹配点、缺口和风险，由用户明确选择单个岗位，并生成与公司、职位和链接绑定的本地选岗记录；记录缺失或不一致时流程停止。

Issue #25 的只读探测已把 Bonjour 选为首个直接投递候选，Watcha 为第二顺位，JobRadar 只作岗位发现源。详细证据见 [外部招聘网站可行性探测](docs/external-site-feasibility-issue-08.md)。在 Codex 侧边栏完成真实预演前，不增加站点适配器抽象。

第三方项目只借鉴设计，不复制代码；来源、许可证和取舍见 [第三方求职 Skill 借鉴记录](docs/third-party-feature-audit.md)。

外部岗位发现统一运行 `apply-external-jobs/scripts/external_jobs.py`：Bonjour 读取公开职位页随页面返回的岗位数据，Watcha 读取其公开 feed，JobRadar 准确返回免费预览/会员限制。浏览器只负责选岗后的详情、登录和申请，不再用页面加载是否超时判断整个平台可用性。

V1 不包含候选人平台账号、积分付费、三个外部网站稳定适配或验证码绕过。WorkBuddy 当前只验收主 Skill 可安装、触发并进入材料采集。

`$职业资产` 是必需依赖，当前来源为 [Ivor-NCUT/career-assets-skill](https://github.com/Ivor-NCUT/career-assets-skill)。本仓库不复制该独立仓库；测试环境必须先确认 Codex 能发现名为“职业资产”的 Skill，否则主流程应停止并报告依赖缺失。

## 安装

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R apply-external-jobs "${CODEX_HOME:-$HOME/.codex}/skills/apply-external-jobs"
cp -R fanhan-job-agent "${CODEX_HOME:-$HOME/.codex}/skills/fanhan-job-agent"
```

安装后在 Codex 中说：

```text
使用 $fanhan-job-agent 帮我找适合的工作，这是我的简历。
```

职业主档、机器可读档案、岗位建议、选岗记录和投递日志都写入 `.fanhan-job-agent/`；待投递 HTML/PDF 只写入 `.fanhan-job-agent/outbox/`。日志不得保存简历正文、联系方式、凭据或表单答案。

## 本地验证

```bash
python3 apply-external-jobs/scripts/application_log.py self-test
python3 apply-external-jobs/scripts/confirmation_gate.py self-test
python3 apply-external-jobs/scripts/external_jobs.py --self-test
python3 apply-external-jobs/scripts/watcha_jobs.py --self-test
python3 fanhan-job-agent/scripts/profile_status.py --self-test
python3 fanhan-job-agent/scripts/match_guard.py --self-test
python3 fanhan-job-agent/scripts/material_gate.py --self-test
node fanhan-job-agent/assets/resume-editor.js --self-test
python3 fanhan-job-agent/scripts/candidate_memory.py self-test
python3 fanhan-job-agent/scripts/local_memory.py --self-test
python3 fanhan-job-agent/scripts/workbench_client.py self-test
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" fanhan-job-agent
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" apply-external-jobs
```

真实验收还需要测试者提供可用于申请的真实材料，并在泛函入库、外部个人数据发送、登录/验证码和最终提交时亲自确认。

## 工作台接入

泛函主链路的接口、评分和缺口以 [工作台接入审计](docs/workbench-integration-audit.md) 为准。当前外部网站安全骨架可以继续复用；候选人自助入库、本人匹配结果回读和首次内部飞书通知已经通过工作台公开接口与通知队列完成，开源 Skill 不携带服务密钥。
