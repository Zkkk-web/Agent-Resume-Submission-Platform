# Agent Resume Submission Platform — V1

V1 是一个可安装到 Codex 的 JobRadar 求职投递 Skill：读取用户明确提供的材料和偏好，在 Codex 内置浏览器中找岗位、协助填写，并在每个岗位最终提交前请求确认。

V1 不包含 WorkBuddy、云端账号、数据库、积分付费、真人推荐或系统默认浏览器自动化。

## 安装

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R apply-jobradar "${CODEX_HOME:-$HOME/.codex}/skills/apply-jobradar"
```

安装后在 Codex 中说：

```text
使用 $apply-jobradar，根据我的简历和求职偏好，从 JobRadar 找合适岗位。提交任何申请前都要让我逐个确认。
```

最小投递记录默认写入当前工作区 `.jobradar/applications.jsonl`，只保存岗位、状态和成功证据等非敏感字段。

## 本地验证

```bash
python3 apply-jobradar/scripts/application_log.py self-test
python3 apply-jobradar/scripts/confirmation_gate.py self-test
```

真实验收还需要测试者提供可用于申请的真实材料，并在个人数据发送、登录/验证码和最终提交时亲自确认。
