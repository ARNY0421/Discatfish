# Discatfish

Discord のユーザー ID と X (Twitter) のアカウントを紐づけて管理するためのツールです。

## 主要機能

- スラッシュコマンド連携: /link コマンドで個別の連携 URL を生成。
- 署名付き URL (HMAC): タイムスタンプと署名により、URL の改ざんやなりすましを防止。
- モダンな Web UI: X Blue を基調としたダークモード対応の洗練されたデザイン。
- SQLite データベース: 連携情報は軽量な SQLite に保存され、簡単にエクスポート可能。

## 必要条件

- Python 3.8 以上
- 24時間稼働可能な Linux サーバー (Ubuntu, Debian, CentOS 等)
- Discord 開発者ポータルのボットアカウント
- X (Twitter) 開発者ポータルの API アカウント (Free 以上)

## セットアップ手順

### 1. 準備
リポジトリからファイルをダウンロードして展開し、そのフォルダ内で以下のコマンドを実行して必要なライブラリをインストールしてください。

```bash
pip install -r requirements.txt
```

### 2. 環境設定 (.env)
.env ファイルを作成し、以下の項目を設定してください

```env
DISCORD_BOT_TOKEN=Discordのボットトークン
X_CLIENT_ID=XのクライアントID
X_CLIENT_SECRET=Xのクライアントシークレット
SIGNING_SECRET=推測されにくい適当な文字列
BASE_URL=http://あなたのサーバーのIPまたはドメイン
FLASK_SECRET_KEY=適当な文字列
```

### 3. API ポータルの設定

#### Discord Developer Portal
- Bot: MESSAGE CONTENT INTENT を有効にします。
- OAuth2: applications.commands スコープを付けてボットをサーバーに招待します。

#### X Developer Portal
- User authentication settings:
    - App type: Web App, Native App, or Additional Client
    - App permissions: Read
    - Callback URI: http://あなたのサーバーのIPまたはドメイン/callback
    - Website URL: https://your-website.com (任意の公開URL。ご自身のGitHubプロフィールなどで構いません)

### 4. 実行

app.pyとbot.pyを起動してください。

## ディレクトリ構成

- app.py: Flask ウェブサーバー（OAuth 処理）
- bot.py: Discord ボット（スラッシュコマンド）
- database.py: データベース操作ロジック
- requirements.txt: 必要ライブラリ一覧
- templates/: HTML テンプレート
- linker.db: ユーザー対応表（自動生成）

## ライセンス

MIT License
