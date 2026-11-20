# cubicles-watch

盯 `cubicles.cloud` 的免费机位：`GET https://api.cubicles.cloud/api/v1/catalog` 里
`freePlan.available` 从 `false` 变 `true` 时，推一条 Telegram，其余时间完全静默。

- 账号：`btpp05@gmail.com`（2026-11-20 注册，已邮箱验证）
- 免费规格：Standard 4 vCPU / 8 GB / 64 GB NVMe，法兰克福，1 Gbps 不限流量
- 限制：每账号 1 台；**建机时要绑卡（页面标注永不扣款）**
- 现状：全部 sold out（后端 3 台母鸡，BigChungus 差 1 GiB 就能开 Standard）

## 部署（只需两步）

### 1. Secrets
仓库 Settings → Secrets and variables → Actions，加两个：

| Name | 值 |
| --- | --- |
| `TG_BOT_TOKEN` | @btppnode_bot 的 token |
| `TG_CHAT_ID` | `644320820` |

### 2. 外腿（GitHub 原生 schedule 不可靠）
cron-job.org 建任务，每 5–10 分钟 POST：

```
URL:    https://api.github.com/repos/btpp03/cubicles-watch/actions/workflows/watch.yml/dispatches
Method: POST
Header: Authorization: Bearer <PAT, 需 repo 权限>
Header: Accept: application/vnd.github+json
Body:   {"ref":"main"}
```

## 手动跑
```bash
export GH_TOKEN=$(cat /root/.gh_tok)
gh workflow run watch.yml -R btpp03/cubicles-watch
gh run watch -R btpp03/cubicles-watch
```
