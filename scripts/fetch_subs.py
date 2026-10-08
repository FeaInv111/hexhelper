"""拉取合集每期的 AI 字幕，存为纯文本 data/subs/<bvid>.txt"""
import json, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSDATA = (ROOT / ".sessdata").read_text().strip()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Cookie": f"SESSDATA={SESSDATA}",
}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

eps = json.loads((ROOT / "episodes.json").read_text())["episodes"]
out = ROOT / "data/subs"
for ep in eps:
    f = out / f"{ep['bvid']}.txt"
    if f.exists():
        continue
    info = get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={ep['bvid']}&cid={ep['cid']}")
    subs = info["data"]["subtitle"]["subtitles"]
    if not subs:
        print("无字幕", ep["bvid"], ep["title"])
        continue
    body = get("https:" + subs[0]["subtitle_url"])["body"]
    f.write_text("\n".join(b["content"] for b in body))
    print("ok", ep["bvid"], ep["title"], len(body))
    time.sleep(0.5)
