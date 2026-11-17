# MallBoard — Debian 12 + 宝塔部署手顺

対象は Debian 12 の VPS と宝塔面板です。公開通信は宝塔の Nginx を通し、アプリは `127.0.0.1:8000` のみにバインドします。MySQL は Compose 内部ネットワークだけで使用し、データは named volume `mysql-data` に保存します。初回起動時にアプリがテーブル作成と架空のデモデータ投入を自動で行うため、手動の seed コマンドは不要です。

## 0. 事前準備

ドメインの DNS A レコードを VPS の IP アドレスへ向け、宝塔のセキュリティ設定・VPS のファイアウォールで TCP 80/443 を許可します。MySQL の 3306 番ポートは開放しません。

**期待結果:** ドメインが VPS の IP に解決され、HTTP/HTTPS の受信が許可されていること。

## 1. Docker と Compose をインストール

VPS に SSH 接続し、Docker 公式 Debian リポジトリから Engine と Compose plugin をインストールします。

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
docker --version
docker compose version
systemctl is-enabled docker
```

**期待結果:** Docker と Docker Compose のバージョンが表示され、最後のコマンドが `enabled` を返すこと。Docker はサーバー起動時に自動起動します。

## 2. アプリをアップロードして展開

交付物の ZIP/TAR を VPS にアップロードします。以下は TAR.GZ の例です。ZIP の場合は `unzip` を使い、リポジトリのルート（`Dockerfile` と `docker-compose.yml` がある階層）を `/opt/mallboard` に展開してください。

```bash
sudo mkdir -p /opt/mallboard
sudo tar -xzf MallBoard-delivery.tar.gz -C /opt/mallboard --strip-components=1
cd /opt/mallboard
ls -la
```

**期待結果:** `Dockerfile`、`docker-compose.yml`、`.env.example`、`backend/`、`frontend/`、`DEPLOY.md` が表示されること。サーバーに Node.js や PDF ソフトをインストールする必要はありません。フロントエンド `dist` と PDF 生成用 WeasyPrint/Pango/HarfBuzz/Noto CJK フォントは Docker のビルド時にアプリイメージへ含まれます。

## 3. `.env` を設定

```bash
cd /opt/mallboard
cp .env.example .env
nano .env
chmod 600 .env
awk -F= '/^(DB_NAME|DB_USER|DB_PASSWORD|MYSQL_ROOT_PASSWORD|DEMO_MODE)=/ {print $1 " は設定済み"}' .env
stat -c '%a %n' .env
```

`DB_NAME` と `DB_USER` は英数字とアンダースコアで指定し、`DB_PASSWORD` と `MYSQL_ROOT_PASSWORD` はそれぞれ別の長いランダム値に置き換えます。例の値のまま運用しないでください。`openssl rand -hex 32` で値を生成できます。`.env` は Git に登録せず、バックアップもアクセス制限してください。

`DEMO_MODE=true` は演示アカウント選択と、顧問・店長・本社／経理・社長のロール切替を有効にするパスワード不要の演示専用モードです。一般公開の本番運用では `false` にし、通常の社員番号・パスワード認証を使用してください。`true` のまま公開する場合は、アクセス元を制限した演示環境として扱ってください。

**期待結果:** `.env` の5項目名が表示され、権限表示が `600 .env` になること。パスワード値は以後の画面出力やチャットへ貼り付けないでください。

## 4. Compose でビルド・起動

```bash
cd /opt/mallboard
sudo docker compose up -d --build
sudo docker compose ps
curl -fsS http://127.0.0.1:8000/api/health
```

初回は React のビルド、MySQL 初期化のため数分かかることがあります。Compose は MySQL の healthcheck が成功してからアプリを起動します。アプリ起動時に空の MySQL データベースへテーブルとデモデータを投入します。

PDF 一覧レポートは Settings のデータ入出力から作成できます。PDF レンダリング依存関係と日本語・中文フォントはアプリイメージにインストールされます。コンテナ再ビルド時の apt/pip 取得にはインターネット接続が必要です。

**期待結果:** `app` と `mysql` の両方が `Up` / `healthy` になり、health API が `{"status":"ok"}` を返すこと。MySQL コンテナに公開ポート設定がなく、ホストの 3306 番ポートでは接続できないこと。初回の状態確認は `sudo docker compose logs --tail=100 app mysql` で行えます。

両サービスには `restart: always` を設定しています。Docker デーモンとコンテナは VPS 再起動後に自動復帰します。

## 5. 宝塔でサイトとリバースプロキシを設定

1. 宝塔面板の「网站」→「添加站点」で対象ドメインのサイトを作成します。
2. 作成したサイトの「设置」→「反向代理」でプロキシを追加します。
3. 目标 URL を `http://127.0.0.1:8000` にし、送信先 Host を `$host` に設定します。宝塔の標準リバースプロキシが `X-Real-IP` / `X-Forwarded-For` を引き継ぐ設定も有効にします。
4. サイトの設定画面で Let's Encrypt 証明書を申請し、ドメインの検証成功後に HTTPS と「HTTP を HTTPS にリダイレクト」を有効にします。

**期待結果:** 宝塔のサイト設定でプロキシ先が `127.0.0.1:8000` と表示され、証明書の状態が有効になること。公開するのは宝塔経由の 80/443 のみです。

## 6. HTTPS の演示確認

```bash
curl -I https://demo.example.com
curl -fsS https://demo.example.com/api/health
```

`demo.example.com` は設定したドメインに置き換えます。

**期待結果:** HTTPS が成功し、health API が `{"status":"ok"}` を返すこと。ブラウザーで演示ページを開き、顧問・店長・本社／経理・社長の役割ごとに Dashboard の待ち件数が切り替わることを確認します。初期表示言語は日本語で、右上の言語切替で中文表示にもできます。

演示链は Households の `HH-D020`（住宅会社 3 社への並行紹介）→ Introductions で各商談を確認→ Revenue で契約・着工情報を確認し、証跡を入力して着工確認→ FeeEntitlement の根拠を確認→本社／経理ロールで承認・請求データ生成・請求・入金へ進めます。店舗名は店舗A〜L、住宅会社名は住宅会社A〜Lで、実在企業名は使いません。Settings からデモデータをリセットすると HH-D001〜HH-D060 など規定の演示データへ戻ります。

## 7. VPS 再起動・自動復帰・データ永続性の確認

先にブラウザーで世帯や報酬の状態を確認してから VPS を再起動します。

```bash
sudo reboot
```

SSH 再接続後:

```bash
sudo systemctl is-active docker
cd /opt/mallboard
sudo docker compose ps
curl -fsS https://demo.example.com/api/health
sudo docker volume ls | grep mysql-data
```

**期待結果:** Docker が `active`、両コンテナが稼働中、HTTPS health API が `{"status":"ok"}` を返し、`mysql-data` volume が存在すること。ブラウザーでリロードして再起動前の操作データが残っていることを確認します。

## 運用上の注意

- アプリ・DB を停止する場合は `sudo docker compose down` を実行します。named volume は保持されます。
- `sudo docker compose down -v` は MySQL volume と保存データを削除するため実行しないでください。
- 更新版を配布した場合は、バックアップ後に `sudo docker compose up -d --build` で再ビルドします。
- DB パスワードを変更する際は `.env` と MySQL 側のユーザー認証を同時に更新してください。MySQL 初期化時に作成したユーザーのパスワードは、`.env` だけ変更しても既存 volume 上では自動変更されません。
- このプロトタイプは実顧客情報・本番業務データを扱う設計ではありません。外部公開前に OS、宝塔、Docker の更新と `.env`・DB バックアップを整備してください。
