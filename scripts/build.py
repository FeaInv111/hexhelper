"""合并英雄、外号、卡片数据 → site/data.js，并下载卡片用到的装备/海克斯图标"""
import json, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pypinyin import lazy_pinyin, Style

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "data/ref"
SITE = ROOT / "site"
CDRAGON = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default"


def icon_url(path):
    # /lol-game-data/assets/ASSETS/... → .../global/default/assets/...（cdragon 路径全小写）
    return CDRAGON + "/" + path.replace("/lol-game-data/assets/", "").lower()


def fetch_icon(url, dest, size):
    if dest.exists():
        return True
    tmp = dest.with_suffix(".tmp")
    if subprocess.run(["curl", "-sfL", "-m", "30", "-o", str(tmp), url]).returncode != 0:
        print("图标下载失败", url)
        return False
    # 保留 PNG：海克斯图标是透明底，转 JPG 会变白
    subprocess.run(["sips", "-Z", str(size), str(tmp), "--out", str(dest)], capture_output=True)
    tmp.unlink()
    return dest.exists()


def search_keys(*words):
    keys = set()
    for w in words:
        w = w.strip().lower()
        if not w:
            continue
        keys.add(w)
        if re.search(r"[一-鿿]", w):
            keys.add("".join(lazy_pinyin(w)))
            keys.add("".join(lazy_pinyin(w, style=Style.FIRST_LETTER)))
    return sorted(keys)


def main():
    champs_raw = [c for c in json.loads((REF / "champs_raw.json").read_text()) if 0 < c["id"] < 1000]
    aliases = json.loads((ROOT / "data/aliases.json").read_text())
    episodes = json.loads((ROOT / "episodes.json").read_text())["episodes"]
    items_raw = json.loads((REF / "items_raw.json").read_text())
    augs_raw = json.loads((REF / "augments_raw.json").read_text())

    item_icon = {}
    for it in sorted(items_raw, key=lambda x: (not x.get("inStore"), x["id"])):
        item_icon.setdefault(it["name"].strip(), (it["id"], it["iconPath"]))
    rarity_key = {"kPrismatic": "prismatic", "kGold": "gold", "kSilver": "silver"}
    aug_icon = {}
    for a in augs_raw:
        name = a["nameTRA"].strip()
        aug_icon.setdefault((name, rarity_key.get(a["rarity"])), (a["id"], a["augmentSmallIconPath"]))
        aug_icon.setdefault((name, None), (a["id"], a["augmentSmallIconPath"]))

    jobs = {}  # 图标键（装备名 / "aug:"+海克斯名）→ (url, 本地路径)

    def item(name):
        if name not in jobs and name in item_icon:
            iid, path = item_icon[name]
            jobs[name] = (icon_url(path), SITE / "img/item" / f"{iid}.png")
        return name

    def aug(name, rarity):
        key = (name, rarity) if (name, rarity) in aug_icon else (name, None)
        if ("aug:" + name) not in jobs and key in aug_icon:
            aid, path = aug_icon[key]
            jobs["aug:" + name] = (icon_url(path), SITE / "img/aug" / f"{aid}.png")
        return name

    (SITE / "img/item").mkdir(parents=True, exist_ok=True)
    (SITE / "img/aug").mkdir(parents=True, exist_ok=True)

    guides = {}  # champion_id → [卡片…]，新的在前
    for ep in episodes:
        card_file = ROOT / "data/cards" / f"{ep['bvid']}.json"
        if not card_file.exists():
            print("缺卡片", ep["bvid"], ep["title"])
            continue
        card = json.loads(card_file.read_text())
        for b in card.get("build", []):
            b["items"] = [item(n) for n in b["items"]]
        for r, names in card.get("augments", {}).items():
            card["augments"][r] = [aug(n, r) for n in names]
        card.pop("uncertain", None)
        card.update(title=ep["title"], pubdate=ep["pubdate"])
        guides.setdefault(card.pop("champion_id"), []).append(card)
    with ThreadPoolExecutor(16) as pool:
        ok = dict(zip(jobs, pool.map(lambda j: fetch_icon(j[0], j[1], 48), jobs.values())))
    icons = {k: str(dest.relative_to(SITE)) for k, (_, dest) in jobs.items() if ok[k]}

    for lst in guides.values():
        lst.sort(key=lambda c: -c["pubdate"])

    champions = []
    for c in champs_raw:
        al = aliases.get(c["alias"], [])
        champions.append({
            "id": c["id"], "key": c["alias"], "name": c["description"], "title": c["name"],
            "aliases": al, "keys": search_keys(c["description"], c["name"], c["alias"], *al),
        })
    champions.sort(key=lambda c: lazy_pinyin(c["name"]))

    nick = json.loads((ROOT / "data/item_nicknames.json").read_text())
    data = {"champions": champions, "guides": guides, "icons": icons, "nick": nick}
    (SITE / "data.js").write_text("window.HEX_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"英雄 {len(champions)}，有攻略 {len(guides)}，图标 {len(icons)}")


if __name__ == "__main__":
    main()
