#!/usr/bin/env python3
"""
Markdown → HTML変換スクリプト

入力: goals/とreviews/配下のMarkdownファイル
出力: docs/配下のHTMLファイル
機能: ダッシュボード生成、進捗グラフ生成、統計情報集計
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
import markdown
from jinja2 import Template

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
GOALS_DIR = PROJECT_ROOT / "goals"
REVIEWS_DIR = PROJECT_ROOT / "reviews"


def convert_md_to_html(md_content: str) -> str:
    """
    Markdown → HTML変換
    
    入力: Markdownテキスト
    出力: HTML文字列
    """
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite'])
    return md.convert(md_content)


def create_dashboard():
    """
    ダッシュボード（index.html）を生成
    
    機能:
    - 現在の半期を表示
    - 統計サマリーを表示
    - 目標・振り返りへのリンク集を表示
    """
    # 現在の半期を判定
    now = datetime.now()
    year = now.year
    half = "H1" if now.month <= 8 else "H2"
    current_period = f"{year}-{half}"
    
    # 統計情報を集計
    stats = {
        "current_period": current_period,
        "goals_count": len(list(GOALS_DIR.glob("*.md"))),
        "reviews_count": len(list(REVIEWS_DIR.rglob("*.md"))),
    }
    
    # 目標ファイル一覧
    goals = []
    for goal_file in sorted(GOALS_DIR.glob("*.md"), reverse=True):
        goals.append({
            "name": goal_file.stem,
            "path": f"goals/{goal_file.stem}.html"
        })
    
    # 振り返りファイル一覧
    reviews = {"weekly": [], "monthly": []}
    for review_file in sorted((REVIEWS_DIR / "weekly").glob("*.md"), reverse=True):
        reviews["weekly"].append({
            "name": review_file.stem,
            "path": f"reviews/weekly/{review_file.stem}.html"
        })
    for review_file in sorted((REVIEWS_DIR / "monthly").glob("*.md"), reverse=True):
        reviews["monthly"].append({
            "name": review_file.stem,
            "path": f"reviews/monthly/{review_file.stem}.html"
        })
    
    # HTMLテンプレート
    template = Template("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xincere-review - ダッシュボード</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <header>
        <h1>📊 xincere-review</h1>
        <p>人事評価プロセス管理システム</p>
    </header>
    
    <main>
        <section class="current-period">
            <h2>現在の評価期間</h2>
            <div class="period-badge">{{ stats.current_period }}</div>
        </section>
        
        <section class="stats">
            <h2>統計サマリー</h2>
            <div class="stat-cards">
                <div class="stat-card">
                    <div class="stat-value">{{ stats.goals_count }}</div>
                    <div class="stat-label">目標ファイル</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.reviews_count }}</div>
                    <div class="stat-label">振り返りファイル</div>
                </div>
            </div>
        </section>
        
        <section class="links">
            <h2>🎯 目標</h2>
            <ul class="file-list">
                {% for goal in goals %}
                <li><a href="{{ goal.path }}">{{ goal.name }}</a></li>
                {% endfor %}
            </ul>
            
            <h2>📅 振り返り</h2>
            <h3>週次</h3>
            <ul class="file-list">
                {% for review in reviews.weekly %}
                <li><a href="{{ review.path }}">{{ review.name }}</a></li>
                {% endfor %}
            </ul>
            
            <h3>月次</h3>
            <ul class="file-list">
                {% for review in reviews.monthly %}
                <li><a href="{{ review.path }}">{{ review.name }}</a></li>
                {% endfor %}
            </ul>
        </section>
    </main>
    
    <footer>
        <p>Generated: {{ generated_at }}</p>
    </footer>
</body>
</html>""")
    
    html = template.render(
        stats=stats,
        goals=goals,
        reviews=reviews,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 出力
    output_file = DOCS_DIR / "index.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"✅ ダッシュボード生成: {output_file}")


def generate_goal_html(md_file: Path):
    """
    目標Markdown → HTMLに変換
    
    入力: goals/配下のMarkdownファイル
    出力: docs/goals/配下のHTMLファイル
    """
    md_content = md_file.read_text(encoding="utf-8")
    html_content = convert_md_to_html(md_content)
    
    template = Template("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - xincere-review</title>
    <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
    <header>
        <h1><a href="../index.html">📊 xincere-review</a></h1>
        <p>{{ title }}</p>
    </header>
    
    <main class="content">
        {{ content | safe }}
    </main>
    
    <footer>
        <p><a href="../index.html">← ダッシュボードに戻る</a></p>
        <p>Generated: {{ generated_at }}</p>
    </footer>
</body>
</html>""")
    
    html = template.render(
        title=md_file.stem,
        content=html_content,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    output_file = DOCS_DIR / "goals" / f"{md_file.stem}.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"✅ 目標HTML生成: {output_file}")


def generate_review_html(md_file: Path, review_type: str):
    """
    振り返りMarkdown → HTMLに変換
    
    入力: reviews/配下のMarkdownファイル
    出力: docs/reviews/配下のHTMLファイル
    機能: 達成度の視覚化
    """
    md_content = md_file.read_text(encoding="utf-8")
    
    # 達成度を抽出（✅/❌/⚠️）
    completed = md_content.count("✅")
    failed = md_content.count("❌")
    partial = md_content.count("⚠️")
    total = completed + failed + partial
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    html_content = convert_md_to_html(md_content)
    
    template = Template("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - xincere-review</title>
    <link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
    <header>
        <h1><a href="../../index.html">📊 xincere-review</a></h1>
        <p>{{ title }}</p>
    </header>
    
    <main class="content">
        <section class="progress">
            <h2>達成度</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ completion_rate }}%"></div>
            </div>
            <p class="progress-text">{{ completion_rate | round(1) }}% ({{ completed }}/{{ total }})</p>
            <div class="status-badges">
                <span class="badge success">✅ 完了: {{ completed }}</span>
                <span class="badge warning">⚠️ 一部: {{ partial }}</span>
                <span class="badge danger">❌ 未完了: {{ failed }}</span>
            </div>
        </section>
        
        {{ content | safe }}
    </main>
    
    <footer>
        <p><a href="../../index.html">← ダッシュボードに戻る</a></p>
        <p>Generated: {{ generated_at }}</p>
    </footer>
</body>
</html>""")
    
    html = template.render(
        title=md_file.stem,
        content=html_content,
        completed=completed,
        failed=failed,
        partial=partial,
        total=total,
        completion_rate=completion_rate,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    output_file = DOCS_DIR / "reviews" / review_type / f"{md_file.stem}.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"✅ 振り返りHTML生成: {output_file}")


def main():
    """メイン処理"""
    print("🚀 HTML生成を開始します...")
    
    # ダッシュボード生成
    create_dashboard()
    
    # 目標HTML生成
    for md_file in GOALS_DIR.glob("*.md"):
        generate_goal_html(md_file)
    
    # 週次振り返りHTML生成
    for md_file in (REVIEWS_DIR / "weekly").glob("*.md"):
        generate_review_html(md_file, "weekly")
    
    # 月次振り返りHTML生成
    for md_file in (REVIEWS_DIR / "monthly").glob("*.md"):
        generate_review_html(md_file, "monthly")
    
    print("✨ HTML生成が完了しました！")


if __name__ == "__main__":
    main()

