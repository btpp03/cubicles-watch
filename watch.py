#!/usr/bin/env python3
"""Cubicles(cubicles.cloud) 免费机位盯梢。
只做一件事：免费 Standard 从「没有」变成「有」时推一条 Telegram，其余时间静默。
状态存 status.json 跟着仓库走，避免重复推。
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.cubicles.cloud/api/v1/catalog"
STATE = "status.json"
REPO = os.environ.get("GITHUB_REPOSITORY", "btpp03/cubicles-watch")
REPO_URL = "https://github.com/" + REPO


def log(*a):
    print(*a, flush=True)


def bj():
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 8 * 3600))


def fetch():
    req = urllib.request.Request(API, headers={"User-Agent": "cubicles-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def tg(text):
    tok = os.environ.get("TG_BOT_TOKEN", "").strip()
    chat = os.environ.get("TG_CHAT_ID", "").strip()
    if not tok or not chat:
        log("[tg] 未配置 TG_BOT_TOKEN/TG_CHAT_ID，跳过通知")
        return False
    data = {"chat_id": chat, "text": text, "parse_mode": "HTML",
            "disable_web_page_preview": "true"}
    th = os.environ.get("TG_THREAD_ID", "").strip()
    if th:
        data["message_thread_id"] = th
    req = urllib.request.Request(
        "https://api.telegram.org/bot%s/sendMessage" % tok,
        data=urllib.parse.urlencode(data).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            res = json.loads(r.read().decode())
        log("[tg] ok=", res.get("ok"), res.get("description", ""))
        return bool(res.get("ok"))
    except Exception as e:
        log("[tg] 失败:", e)
        return False


def main():
    data = fetch()
    free = data.get("freePlan") or {}
    plans = data.get("plans") or []
    free_ok = bool(free.get("available"))
    paid_ok = [p["id"] for p in plans if p.get("available")]

    st = load_state()
    prev = st.get("free_available")
    st["free_available"] = free_ok
    st["plans_available"] = paid_ok
    st["checked_at"] = int(time.time())

    detail = free.get("details") or []
    hint = "; ".join(d.get("message", "") for d in detail if d.get("message"))
    reason = free.get("reason") or ""

    log("free_available=%s reason=%s paid=%s" % (free_ok, reason, paid_ok))

    if free_ok and prev is not True:
        msg = (
            "🟢 <b>Cubicles 免费机位放出来了</b>\n"
            "规格：Standard 4 vCPU / 8 GB / 64 GB NVMe（法兰克福，1 Gbps 不限流量）\n"
            "限制：每账号 1 台，<b>需要绑卡（标注永不扣款）</b>\n"
            "去建机：https://cubicles.cloud/start?task=custom&plan=standard\n"
            "已注册账号：btpp05@gmail.com\n"
            "仓库：" + REPO_URL + "\n"
            "时间：" + bj() + "（北京时间）"
        )
        tg(msg)
        st["last_notify"] = int(time.time())
    elif paid_ok and not free_ok and st.get("last_paid_note") != ",".join(paid_ok):
        log("付费档可买：%s（不推送，仅记录）" % paid_ok)

    st["last_paid_note"] = ",".join(paid_ok)
    json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
    log("state 已写回")


if __name__ == "__main__":
    main()
