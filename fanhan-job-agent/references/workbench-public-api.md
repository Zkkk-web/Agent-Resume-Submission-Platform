# 工作台公开接口契约

基线：`Ivor-NCUT/ai-recruiting-workbench` Issue #326 与 #331。默认服务地址为 `https://fanhan-workbench.zeabur.app`；如用户或测试环境提供 `FANHAN_WORKBENCH_URL`，优先使用该地址。

## 安全边界

- Skill 只调用 `/api/public/*` 候选人自助入口，不携带 `WORKBENCH_DATABASE_API_TOKEN` 或 `WORKBENCH_CANDIDATE_INGEST_TOKEN`。
- `client_token` 是候选人本地生成的随机会话标识，只用于幂等和查询本人本次申请；不得打印、提交到 Git 或写入普通投递日志。
- 文件上传和申请创建都必须发生在候选人明确授权之后。

## 请求顺序

1. `GET /healthz`：未 ready 时停止写入。
2. `GET /api/public/jobs`：读取脱敏后的真实开放岗位。
3. `POST /api/public/candidate-files?name=<文件名>`：请求体为 PDF 原始字节，`Content-Type: application/pdf`，最大 10 MB。
4. `POST /api/public/candidate-applications`：JSON 字段如下。

```json
{
  "job_id": "真实岗位 ID",
  "file_id": "上传返回的文件 ID",
  "client_token": "本地随机会话标识",
  "portfolio_url": "可选的 HTTP(S) 链接",
  "self_introduction": "候选人确认过的自荐说明",
  "consent_confirmed": true
}
```

5. `GET /api/public/candidate-applications/<申请 ID>`，请求头 `X-Application-Client-Token` 使用同一会话标识，读取 `processing`、`completed` 或失败状态。

## 结果解释

- 重复请求返回同一个申请，不代表创建第二名候选人。
- `completed` 表示候选人材料已完成工作台处理；资料待补充时可以没有岗位匹配。
- 只有资料可匹配时才生成 `pending` 匹配审核，绝不自动批准或发送给企业。
- `match` 非空时只包含本次候选人 × 岗位的脱敏结果：`score`、`algorithm_version`、`reason`、`hard_filter_summary`、`keywords`、`evidence` 和 `risks`。它是工作台保存的真实结果，只能在候选人授权提交后回读，不得在 Skill 中重算。
- 当前公开状态接口仍不返回首次飞书通知回执；该能力完成前不得自行补造通知结果。

公开岗位当前稳定字段是 `id`、`company`、`title`、`summary`、`description`、`category`、`city`、`work_type`、`salary` 和 `required_skills`。`work_mode`、`relocation_required`、`required_start_date` 和 `work_authorization` 缺失时必须标记未知，不能推断为符合。
