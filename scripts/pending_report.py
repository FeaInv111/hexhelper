"""生成 待确认.md：缺内容的卡片 + 各卡片 uncertain 条目"""
import glob, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
eps = {e["bvid"]: e for e in json.loads((ROOT / "episodes.json").read_text())["episodes"]}
champ = {int(l.split("\t")[0]): l.split("\t")[2] for l in (ROOT / "data/ref/champions.txt").read_text().strip().split("\n")}
cards = {c["bvid"]: c for c in (json.load(open(f)) for f in glob.glob(str(ROOT / "data/cards/*.json")))}

out = ["# 待确认清单", "", "字幕是 AI 识别的，下面是整理时拿不准的地方。确认/纠正后告诉我「英雄 + 改成什么」即可。", "", "## 缺内容"]
for bvid, ep in sorted(eps.items(), key=lambda x: x[1]["pubdate"]):
    c = cards.get(bvid)
    if not c:
        out.append(f"- {ep['title']}：没有字幕，整张卡片缺")
        continue
    miss = [k for k, v in [("出装", c["build"]), ("海克斯", any(c["augments"].values())), ("注意事项", c["tips"])] if not v]
    if miss:
        out.append(f"- {champ[c['champion_id']]}：没有{'、'.join(miss)}（视频里没念出来）")
out += ["", "## 识别存疑（按视频发布顺序）", ""]
n = 0
for c in sorted(cards.values(), key=lambda c: eps[c["bvid"]]["pubdate"]):
    if c.get("uncertain"):
        out.append(f"### {champ[c['champion_id']]} — {eps[c['bvid']]['title']}")
        out += [f"- {u}" for u in c["uncertain"]] + [""]
        n += len(c["uncertain"])
(ROOT / "待确认.md").write_text("\n".join(out) + "\n")
print(f"待确认 {n} 条")
