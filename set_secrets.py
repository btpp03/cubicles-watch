
import base64, json, re, urllib.request
from nacl import encoding, public
PAT = open("/root/.gh_tok").read().strip()
REPO = "btpp03/cubicles-watch"
H = {"Authorization": f"token {PAT}", "Accept": "application/vnd.github+json",
     "X-GitHub-Api-Version": "2022-11-28"}
doc = open("/root/.hermes/skills/z-image-generation/references/tg-bot-dual-channel.md", errors="replace").read()
BOT = re.search(r'(\d{8,11}:[A-Za-z0-9_-]{30,40})', doc).group(1)
CHAT = re.search(r'chat_id\s*=\s*`(\d+)`', doc).group(1)
print("bot id:", BOT.split(":")[0], "| chat:", CHAT)
with urllib.request.urlopen(f"https://api.telegram.org/bot{BOT}/getMe", timeout=20) as r:
    me = json.loads(r.read().decode())
print("getMe:", me.get("ok"), me.get("result", {}).get("username"))

def api(url, data=None, method="GET"):
    b = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=b, headers=H, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}

pk = api(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key")
for name, val in [("TG_BOT_TOKEN", BOT), ("TG_CHAT_ID", CHAT)]:
    sealed = public.SealedBox(public.PublicKey(pk["key"], encoding.Base64Encoder)).encrypt(val.encode())
    api(f"https://api.github.com/repos/{REPO}/actions/secrets/{name}",
        {"encrypted_value": base64.b64encode(sealed).decode(), "key_id": pk["key_id"]}, method="PUT")
print("secrets:", [s["name"] for s in api(f"https://api.github.com/repos/{REPO}/actions/secrets").get("secrets", [])])
