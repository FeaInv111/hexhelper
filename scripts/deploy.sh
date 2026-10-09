#!/bin/sh
# 重新构建并发布到 GitHub Pages（gh-pages 分支 = site/ 目录）
set -e
cd "$(dirname "$0")/.."
.venv/bin/python scripts/sync_aliases.py
.venv/bin/python scripts/build.py
.venv/bin/python scripts/alias_report.py
git add -A
git commit -qm "${1:-更新攻略数据}" || true
# 连 GitHub 偶尔抖动，失败重试几次
retry() { for i in 1 2 3 4; do "$@" && return 0; echo "推送失败，重试 $i"; sleep 8; done; return 1; }
retry git push -q origin main
git subtree split --prefix site -b gh-pages -q
retry git push -q -f origin gh-pages
echo "已发布：https://feainv111.github.io/hexhelper/（约 1 分钟后生效）"
