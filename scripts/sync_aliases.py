"""把 外号检查表.md 里手改的外号同步回 data/aliases.json（md 是人工编辑的源）"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "外号检查表.md").read_text()
rows = [l.split("\t") for l in (ROOT / "data/ref/champions.txt").read_text().strip().split("\n") if int(l.split("\t")[0]) < 1000]
key_by_name = {name: key for _, _, name, key in rows}

aliases = {}
for line in md.splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) != 3 or cells[0] in ("英雄", "---"):
        continue
    name = cells[0].lstrip("⭐")
    if name not in key_by_name:
        print("表里有不认识的英雄名:", name)
        continue
    words = [w.strip() for w in cells[2].replace(",", "、").replace("，", "、").split("、")]
    aliases[key_by_name[name]] = [w for w in words if w and w != "—"]

(ROOT / "data/aliases.json").write_text(json.dumps(aliases, ensure_ascii=False, indent=1) + "\n")
print(f"同步 {len(aliases)} 个英雄的外号")
