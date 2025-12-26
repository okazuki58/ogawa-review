#!/bin/bash
#
# GitHub Pagesデプロイスクリプト
#
# 機能:
# 1. HTML生成（generate_html.py実行）
# 2. git commit & push
# 3. GitHub Pages自動反映

set -e  # エラーで停止

echo "🚀 GitHub Pagesデプロイを開始します..."

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# Python仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "⚠️  .venvが見つかりません。Python環境をセットアップしてください。"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Python仮想環境を有効化
source .venv/bin/activate

# HTML生成
echo "📝 HTMLを生成中..."
python3 scripts/generate_html.py

# Gitの変更確認
if [ -z "$(git status --porcelain docs/)" ]; then
    echo "✅ 変更がありません。デプロイをスキップします。"
    exit 0
fi

# Git commit
echo "💾 変更をコミット中..."
git add docs/
git commit -m "docs: Update GitHub Pages ($(date '+%Y-%m-%d %H:%M:%S'))"

# Git push
echo "🚀 GitHub Pagesにプッシュ中..."
git push origin main

echo "✨ デプロイが完了しました！"
echo "📖 GitHub Pages: https://[username].github.io/xincere-review/"
echo ""
echo "💡 GitHub Pagesの設定を確認してください："
echo "   Settings > Pages > Source: main branch, /docs folder"

