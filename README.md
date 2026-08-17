# Agent Resume Submission Platform — V1

V1 由一个泛函求职主 Skill 和一个外部网站探索适配器组成：

- `fanhan-job-agent`：整理真实材料、读取泛函岗位，并在候选人明确授权后通过工作台公开业务 API 幂等入库。
- `apply-jobradar`：在 Codex 内置浏览器中探索 JobRadar 外部投递，并保留个人数据确认与逐岗位最终确认。

V1 不包含候选人平台账号、积分付费、三个外部网站稳定适配或验证码绕过。WorkBuddy 当前只验收主 Skill 可安装、触发并进入材料采集。

## 安装

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R apply-jobradar "${CODEX_HOME:-$HOME/.codex}/skills/apply-jobradar"
cp -R fanhan-job-agent "${CODEX_HOME:-$HOME/.codex}/skills/fanhan-job-agent"
```

安装后在 Codex 中说：

```text
使用 $fanhan-job-agent 读取我的真实求职材料。先说明隐私边界；未经我明确授权，不要上传给泛函或任何招聘网站。
```

主 Skill 的本地生成物写入当前工作区 `.fanhan-job-agent/`；JobRadar 最小投递记录写入 `.jobradar/applications.jsonl`。两者都不得保存简历正文、联系方式、凭据或表单答案。

## 本地验证

```bash
python3 apply-jobradar/scripts/application_log.py self-test
python3 apply-jobradar/scripts/confirmation_gate.py self-test
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" fanhan-job-agent
```

真实验收还需要测试者提供可用于申请的真实材料，并在泛函入库、外部个人数据发送、登录/验证码和最终提交时亲自确认。

## 工作台接入

泛函主链路的接口、评分和缺口以 [工作台接入审计](docs/workbench-integration-audit.md) 为准。当前 JobRadar 安全骨架可以继续复用，但开源 Skill 不能携带工作台服务密钥；候选人自助入库身份、指定候选人岗位评估和首次入库飞书通知需要先在工作台补齐。
