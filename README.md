# MallBoard

住宅相談ビジネスの業務フローを体験できる非公式プロトタイプです。顧客相談、複数住宅会社への紹介と並行商談、契約、実際着工の確認、報酬確定・請求までを操作できます。デモデータはすべて架空です。

## 技術構成

- FastAPI + React (Vite) を単一の `app` コンテナで配信
- MySQL 8 (`utf8mb4`) を別コンテナで稼働し、Compose 内部ネットワークのみで接続
- named volume によるデータ永続化、起動時の自動テーブル作成とデモデータ投入
- 日本語を既定言語として中文へ切替可能

## 起動

Docker と Docker Compose がある環境で、リポジトリのルートから `.env` を用意して起動します。

```sh
cp .env.example .env
# .env の DB_PASSWORD と MYSQL_ROOT_PASSWORD を別々の長いランダム値に変更
docker compose up -d --build
```

アプリは `127.0.0.1:8000` のみに公開されます。VPS での宝塔リバースプロキシ、Let's Encrypt、再起動後の確認手順は [DEPLOY.md](DEPLOY.md) を参照してください。

## デモ操作

1. 初期状態では「顧問」ロールでログインしています。右上から「店長」または「本社・経理」に切り替えます。
2. 「紹介・商談」で佐々木様を選ぶと、青葉ホーム・みらい住建・木の香デザインとの並行商談を確認できます。
3. 「着工・報酬」で店長または本社・経理ロールを選び、実際着工済みの案件に確認証跡を入力して着工確認します。FeeRule v2026.1 に基づく報酬権利が生成されます。
4. 「本社・経理」ロールで報酬を請求済み、入金済みに進められます。争議中の金額は請求へ進められません。
5. 「設定」からデモデータを初期状態に戻せます（本社・経理ロール限定）。

初期デモアカウント:

| ロール | 表示名 |
| --- | --- |
| 顧問 | 佐藤 美咲 |
| 店長 | 田中 健 |
| 本社・経理 | 山本 経理 |

ログインはデモ用のロール切替で、実アカウントやパスワードはありません。

## 開発

API: FastAPI (`backend/main.py`)、UI: React + Vite (`frontend/`)、DB 接続先は環境変数 `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` で設定します。ローカル開発でも MySQL 8 が必要です。

```sh
cd frontend
npm install
npm run dev
```

別ターミナルで API を起動します。Compose の `.env` と同じ MySQL 接続環境変数を設定してください。

```sh
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
