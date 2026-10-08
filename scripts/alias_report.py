"""生成 外号检查表.md，列出每个英雄所有可搜索的叫法，并标出撞名"""
import glob, json
from collections import defaultdict
from pathlib import Path
from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
al = json.loads((ROOT / "data/aliases.json").read_text())
rows = [l.split("\t") for l in (ROOT / "data/ref/champions.txt").read_text().strip().split("\n") if int(l.split("\t")[0]) < 1000]
guided = {json.load(open(f))["champion_id"] for f in glob.glob(str(ROOT / "data/cards/*.json"))}

owner = defaultdict(set)
for i, title, name, key in rows:
    for w in [name, title, *al.get(key, [])]:
        owner[w].add(name)
dup = {w: v for w, v in owner.items() if len(v) > 1}

rows.sort(key=lambda r: lazy_pinyin(r[2]))
out = ["# 英雄搜索词检查表", "",
       "每个英雄能被下面这些词搜到；这些词的**全拼**和**拼音首字母**也能搜（例如 亚索 → yasuo / ys）。",
       "⭐ = 已有攻略。要改直接告诉我「X 加 Y」「X 删 Y」。", ""]
if dup:
    out += ["## ⚠️ 同一个词对应多个英雄", ""] + [f"- {w}：{'、'.join(sorted(v))}" for w, v in dup.items()] + [""]
out += ["## 全部英雄", "", "| 英雄 | 称号 | 外号/简称 |", "|---|---|---|"]
for i, title, name, key in rows:
    out.append(f"| {'⭐' if int(i) in guided else ''}{name} | {title} | {'、'.join(al.get(key, [])) or '—'} |")
(ROOT / "外号检查表.md").write_text("\n".join(out) + "\n")
print("撞名:", dup)
