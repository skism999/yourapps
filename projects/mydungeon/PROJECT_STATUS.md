# My Dungeon プロジェクト - 現状サマリー

**最終更新日**: 2025年12月4日
**プロジェクト状態**: ✅ 本番稼働中（ConoHa VPS）

---

## 📋 プロジェクト概要

**My Dungeon** - 生年月日と時刻から運命のアイテムと必殺技を診断するWebアプリケーション

- **目的**: dungeon.humanjp.com からデータをスクレイピングし、診断結果を画像で出力
- **デプロイ先**: ConoHa VPS（Ubuntu 22.04）
- **アクセス方法**: `http://<ConoHa-IP-Address>`

---

## 🏗 システム構成

### アーキテクチャ
```
[ユーザー] → [Nginx:80] → [FastAPI:8000] → [Playwright] → [dungeon.humanjp.com]
                                ↓
                           [画像生成]
                                ↓
                           [結果表示]
```

### Docker構成
- **mydungeon コンテナ**: FastAPI アプリケーション（Python 3.11）
- **nginx コンテナ**: リバースプロキシ（HTTP/HTTPS）

### 技術スタック

**バックエンド**:
- Python 3.11
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Playwright 1.40.0（Chromium）
- Pillow 10.1.0
- pandas 2.1.3

**フロントエンド**:
- HTML5
- Tailwind CSS（CDN）
- Vanilla JavaScript

**インフラ**:
- Docker + Docker Compose
- Nginx（リバースプロキシ）
- ConoHa VPS

---

## 📁 プロジェクト構造

```
mydungeon/
├── backend/                    # Pythonバックエンド
│   ├── app.py                 # FastAPI メインアプリ
│   ├── scraper.py             # スクレイピング処理
│   ├── data_processor.py      # データ処理・必殺技判定
│   ├── layout_manager.py      # 画像レイアウト管理
│   ├── image_processor.py     # 画像生成処理
│   ├── dungeon_service.py     # 統合サービス
│   ├── models.py              # データモデル
│   ├── config.py              # 設定管理
│   ├── .env                   # 環境変数（Git管理外）
│   └── requirements.txt       # Python依存関係
│
├── frontend/                   # フロントエンド
│   ├── index.html             # 入力画面
│   ├── result.html            # 結果表示画面
│   ├── js/
│   │   └── app.js             # JavaScript処理
│   └── css/
│       └── style.css          # スタイル
│
├── database/                   # データベース
│   ├── csv/
│   │   ├── item_list.csv          # 73アイテム
│   │   ├── hissatsuwaza_list.csv  # 67必殺技
│   │   ├── meaning_of_color.csv   # 色の意味
│   │   └── how_to_action.csv      # 動き方
│   └── images/
│       ├── item/              # アイテム画像
│       └── Hissatsuwaza/      # 必殺技画像
│
├── output/                     # 生成画像保存先（永続化）
│
├── nginx/                      # Nginx設定
│   ├── nginx.conf             # メイン設定
│   ├── conf.d/
│   │   └── mydungeon.conf     # サイト設定
│   └── ssl/                   # SSL証明書用（将来）
│
├── Dockerfile                  # Docker設定
├── docker-compose.yml          # Docker Compose設定
├── deploy.sh                   # デプロイスクリプト
├── CONOHA_DEPLOYMENT_GUIDE.md  # ConoHaデプロイガイド
├── PROJECT_STATUS.md           # このファイル
└── README.md                   # プロジェクト概要
```

---

## ✅ 実装済み機能

### 1. スクレイピング機能
- Playwrightによる自動データ取得
- タイムゾーン対応（Asia/Tokyo）
- エラーハンドリング
- ヘッドレスモード対応

### 2. データ処理
- アイテム情報の取得・マッピング
- 必殺技ペア判定（2枚揃いで必殺技成立）
- 色系統別データ分類

### 3. 画像生成
- アイテム画像: 188px × 250px
- 必殺技画像: 376px × 250px（アイテムの2倍）
- 色系統別レイアウト（赤→緑→青→黄）
- 名前・日時表示
- 日本語フォント対応（Noto CJK）

### 4. Web API（FastAPI）
- `GET /` - トップページ（入力画面）
- `POST /api/generate` - 診断結果生成API
- `GET /api/health` - ヘルスチェック
- `GET /output/{filename}` - 生成画像配信
- `GET /images/{path}` - アイテム画像配信
- `GET /static/{path}` - 静的ファイル配信

### 5. フロントエンド
- レスポンシブデザイン（モバイル対応）
- 生年月日・時刻入力（セレクトボックス）
- 名前入力（任意）
- ローディング表示
- エラーハンドリング
- 診断結果表示
  - 結果画像
  - 取得数字一覧
  - アイテム・必殺技詳細
  - 色ごとの枚数
  - 動き方の説明
- ダウンロード機能
  - 画像ダウンロード（PNG形式）
  - PDFダウンロード（詳細情報付き）
  - モバイル対応（タッチイベント）

### 6. デプロイ・運用
- Docker化
- Nginxリバースプロキシ
- 永続化（database, output）
- 自動デプロイスクリプト
- ConoHa VPS対応

---

## 🔧 最近の修正履歴

### 2025年12月4日
- ✅ モバイルでダウンロードボタンが反応しない問題を修正
- ✅ app.jsにモバイル対応のダウンロード関数を実装
  - モバイル判定とデバイス別処理
  - タッチイベント対応（MouseEvent使用）
  - ダウンロード中の視覚的フィードバック
  - ダブルタップ防止
- ✅ result.htmlでイベントリスナーを適切に設定
  - onclickからaddEventListenerに変更
  - touchendイベント追加
  - 画像・PDFダウンロード両方に対応
- ✅ style.cssにモバイルタッチ操作最適化を追加
  - touch-action: manipulation
  - -webkit-tap-highlight-color設定
  - モバイルでの最小タップエリア確保（48px）

### 2025年11月27日
- ✅ Playwrightブラウザパス問題を修正
- ✅ result pageデザイン更新（ボーダー削除、テキスト色変更）
- ✅ Noto CJKフォント追加（日本語表示対応）
- ✅ 必殺技判定、UI改善
- ✅ Dockerfile最適化

### 2025年11月26日
- ✅ ConoHa VPS デプロイ設定追加
- ✅ Docker + Nginx構成実装
- ✅ デプロイガイド作成

### 2025年11月24日
- ✅ バックエンドコア機能完成
- ✅ フロントエンド実装完了
- ✅ 全機能統合テスト完了

---

## 🚀 ConoHa VPS デプロイ情報

### デプロイ方法

```bash
# SSH接続
ssh root@<ConoHa-IP-Address>

# プロジェクトディレクトリに移動
cd /root/yourapps/projects/mydungeon

# デプロイ実行
./deploy.sh
```

### 環境変数 (backend/.env)

```env
TARGET_URL=https://dungeon.humanjp.com/
HEADLESS=true
PYTHONUNBUFFERED=1
```

### Docker設定

**ポート**:
- Nginx: 80（HTTP）、443（HTTPS - 将来）
- FastAPI: 8000（内部のみ）

**ボリューム**:
- `./database:/app/database:ro` - データベース（読み取り専用）
- `./output:/app/output` - 生成画像（読み書き）

---

## 📝 運用コマンド

### 基本操作

```bash
# コンテナ状態確認
docker-compose ps

# ログ確認
docker-compose logs -f

# ログ確認（特定サービス）
docker-compose logs -f mydungeon

# コンテナ再起動
docker-compose restart

# コンテナ停止
docker-compose down

# コンテナ起動
docker-compose up -d
```

### 更新・デプロイ

```bash
# 最新コードを取得してデプロイ
./deploy.sh

# 手動でビルド
docker-compose build --no-cache

# 手動で起動
docker-compose up -d
```

### デバッグ

```bash
# コンテナ内に入る
docker-compose exec mydungeon bash

# Playwrightブラウザ確認
docker-compose exec mydungeon playwright --version

# Python環境確認
docker-compose exec mydungeon python --version
```

---

## ⚠️ 重要な注意事項

### セキュリティ
- `backend/.env` ファイルはGit管理外（秘密情報）
- SSH接続時は強力なパスワードを使用
- ファイアウォール設定推奨（UFW）

### パフォーマンス
- スクレイピングに最大300秒のタイムアウト設定
- 生成画像は1時間キャッシュ
- 同時アクセス数に注意（VPS 1GBプラン）

### データ
- CSVファイルはUTF-8エンコーディング必須
- 画像ファイルは永続化済み
- 生成画像は `output/` に保存

---

## 🎯 今後の拡張案（オプション）

### 優先度: 高
- [ ] **HTTPS化**（SSL証明書導入）
- [ ] **ドメイン設定**（独自ドメイン）
- [ ] **エラー監視**（ログ監視・アラート）

### 優先度: 中
- [ ] **パフォーマンス改善**（画像圧縮・CDN）
- [ ] **キャッシング強化**（Redis導入）
- [ ] **自動バックアップ**（データベース・生成画像）

### 優先度: 低
- [x] **PDF出力機能**（2025年12月4日実装完了）
- [ ] **SNSシェア機能**
- [ ] **診断履歴保存機能**
- [ ] **ユーザー認証機能**

---

## 🐛 既知の問題

現在、既知の問題はありません。

---

## 📊 テスト済みデータ

以下のデータで動作確認済み:

1. **1991年9月16日13時50分** - 15アイテム、1必殺技 ✅
2. **1997年5月24日20時50分** - 19アイテム、7必殺技 ✅
3. **1991年4月22日11時00分** - 16アイテム、1必殺技 ✅

---

## 📞 トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs

# コンテナを再ビルド
docker-compose build --no-cache
docker-compose up -d
```

### スクレイピングエラー

```bash
# Playwrightブラウザを再インストール
docker-compose exec mydungeon playwright install chromium
docker-compose restart mydungeon
```

### 日本語が文字化けする

- Noto CJKフォントがインストール済みか確認
- CSVファイルのエンコーディングがUTF-8か確認

### 画像が表示されない

```bash
# パーミッション確認
ls -la output/
chmod 755 output

# 画像ファイル確認
ls -la database/images/
```

---

## 💡 次回Claudeセッションで伝えること

プロジェクトは完成・本番稼働中です。以下の内容を伝えてください：

```
「My Dungeonプロジェクトは既にConoHa VPSにデプロイ済みで本番稼働中です。
PROJECT_STATUS.mdに現状がまとめられています。
機能追加や修正がある場合は具体的な要望を教えてください。」
```

---

## 📚 関連ドキュメント

- **README.md** - プロジェクト概要・クイックスタート
- **CONOHA_DEPLOYMENT_GUIDE.md** - ConoHa VPSデプロイ詳細手順
- **PROJECT_STATUS.md** - このファイル（現状サマリー）

---

**プロジェクト完成度**: 100%
**稼働状況**: 本番稼働中
**メンテナンス**: 定期的なログ確認を推奨
