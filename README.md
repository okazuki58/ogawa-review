# xincere-review

人事評価プロセスを半自動化するシステム。プロフィール深掘り→目標設定→自動分解→振り返り→評価のサイクルを、Claude Code skillsとmacloggerで実現します。

## 特徴

- **選択式でユーザーフレンドリー**: 自由入力を最小化し、選択肢から選ぶだけで完了
- **既存情報の最大活用**: グレード・Value・前回評価から自動で選択肢を生成
- **Claude Code skillsで完結**: スクリプトは補助的
- **GitHub Pagesで見やすく**: 評価者にURL共有するだけ
- **macloggerとの自動連携**: 手動入力を最小化
- **目標と振り返りの一貫性**: 目標↔ログ↔振り返りが常に連動

## 前提条件

- Python 3.10以上
- Git
- Claude Code または Codex
- macloggerプロジェクトを同階層（`~/dev/maclogger/`）にクローン済み

## セットアップ

### 1. プロジェクトと依存ツールのクローン

```bash
cd ~/dev
git clone <xincere-review-repo-url> xincere-review
git clone <maclogger-repo-url> maclogger
```

### 2. xincere-reviewのセットアップ

```bash
cd xincere-review

# Python環境セットアップ
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. GitHub Pagesセットアップ

1. GitHubでリポジトリを作成
2. Settings > Pages > Source: `main` branch, `/docs` folder

### 4. 前回評価シートを配置

Google SpreadsheetからCSVエクスポート

```bash
# resources/original-sheets/YYYY-HX/ に保存
# 例: resources/original-sheets/2025H2/FY2025下半期_評価シート_小川一季.csv
```

### 5. maclogger連携

```bash
# シンボリックリンク作成
ln -s ../maclogger/reports ./logs
```

## 使い方

### プロフィール作成（初回のみ）

```bash
# Claude Code起動
claude

> profile-builder skillを使ってプロフィールを作成して
```

選択式の質問に答えていくだけで、`my-profile/`配下にプロフィールが自動生成されます。

質問例:
- Q1. グレードを選んでください → G2 - 作業者
- Q2. エンジニア歴を選んでください → 1-3年
- Q3. 実務経験のある技術を選んでください → React / Next.js
- ...（以下、選択肢から選んでいくだけ）

### 目標設定

```bash
> 今期の半期目標を立てて
```

Claude: 「今期」は 2026-H1（2026/03〜2026/08）でよろしいですか？
→ はい

- 前回評価（2025-H2）を自動読み込み・分析
- 課題を反映した半期目標を提案
- 自動的に月次→週次→日次に分解

### 振り返り

```bash
> 今週の振り返りをして
```

- macloggerログと照合して達成度チェック
- 未達成なら原因分析とfix提案

### GitHub Pagesにデプロイ

```bash
./scripts/deploy.sh
```

生成されたURL: `https://[username].github.io/xincere-review/`

## ディレクトリ構造

```
xincere-review/
├── .claude/skills/
│   ├── profile-builder/          # 選択式プロフィール作成
│   └── performance-review/       # 目標設定・振り返り
├── my-profile/                    # gitignore（個人情報）
├── goals/                         # 目標ファイル
├── reviews/                       # 振り返りファイル
│   ├── monthly/
│   └── weekly/
├── resources/
│   ├── original-sheets/          # 評価シート（gitignore）
│   ├── template/
│   ├── spec/
│   └── work-log/
├── logs/ -> ../maclogger/reports/  # シンボリックリンク
├── docs/                          # GitHub Pages公開用
└── scripts/                       # 自動化スクリプト
```

## 運用フロー

### 半期開始時（年2回）

1. プロフィール更新（必要に応じて）
2. 半期目標設定
3. 自動的に月次→週次→日次に分解

### 毎週金曜日

1. 週次振り返り実行
2. 達成度チェック
3. 未達成ならfix提案
4. 次週の日次目標調整

### 月末

1. 月次振り返り（週次×4を集約）
2. 翌月の週次目標を新規作成

### 半期終了時（年2回）

1. 半期振り返り（月次×6を集約）
2. Value別実績整理
3. 評価予測
4. HTML生成 & GitHub Pagesにデプロイ
5. 評価者に共有（URLを送付）

## トラブルシューティング

### macloggerのログが見つからない

```bash
# シンボリックリンクを確認
ls -la logs/

# macloggerが同階層にあるか確認
ls -la ../maclogger/reports/
```

### HTML生成でエラーが発生

```bash
# Python環境を確認
source .venv/bin/activate
pip install -r requirements.txt

# 手動でHTML生成を実行
python3 scripts/generate_html.py
```

### GitHub Pagesが表示されない

1. Settings > Pages で設定を確認
2. Source: `main` branch, `/docs` folder
3. プライベートリポジトリの場合、有料プランが必要

## ライセンス

社内利用のみ

## サポート

質問やバグ報告は、社内Slackの #xincere-review チャンネルまで。

