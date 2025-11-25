# My Dungeon - 運命の診断アプリ

生年月日と時刻から、あなたの運命のアイテムと必殺技を診断するWebアプリケーション。

## 🌟 機能

- 生年月日・時刻の入力
- 外部サイト(dungeon.humanjp.com)からのデータ取得（スクレイピング）
- アイテムと必殺技の自動判定
- 結果を画像またはPDFで出力
- シンプルでおしゃれなデザイン
- レスポンシブ対応

## 🛠 技術スタック

### フロントエンド
- HTML5
- CSS3 (Tailwind CSS)
- JavaScript (Vanilla)

### バックエンド
- Python 3.11+
- FastAPI
- Playwright (スクレイピング)
- Pillow (画像処理)
- pandas (データ処理)
- reportlab (PDF生成)

### デプロイ
- Docker
- Render (推奨)

## 📁 プロジェクト構造

```
mydungeon/
├── backend/              # Pythonバックエンド
│   ├── app.py           # FastAPIメインアプリ
│   ├── scraper.py       # スクレイピング処理
│   ├── data_processor.py # データ処理
│   ├── image_processor.py # 画像・PDF生成
│   └── requirements.txt
├── frontend/            # フロントエンド
│   ├── index.html       # 入力画面
│   ├── result.html      # 結果表示画面
│   ├── css/
│   └── js/
├── database/            # データベース
│   ├── csv/            # CSVファイル
│   └── images/         # 画像ファイル
├── tests/              # テストコード
├── output/             # 生成ファイル保存先
├── Dockerfile
├── DEVELOPMENT_PLAN.md # 開発手順書（詳細）
└── README.md           # このファイル
```

## 🚀 クイックスタート

### 1. 環境構築

```bash
cd /workspaces/yourapps/projects/mydungeon

# 仮想環境作成
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# パッケージインストール
pip install -r requirements.txt

# Playwrightブラウザインストール
playwright install chromium
```

### 2. ローカル起動

```bash
# バックエンドサーバー起動
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで http://localhost:8000 にアクセス

### 3. テスト実行

```bash
# 単体テスト
pytest tests/ -v
```

## 📖 詳細な開発手順

詳細な開発手順については、[DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) を参照してください。

以下の内容が含まれています：
- Phase 1: 環境構築
- Phase 2: スクレイピング機能実装
- Phase 3: データ処理ロジック実装
- Phase 4: 画像処理実装
- Phase 5: FastAPIバックエンド構築
- Phase 6: フロントエンド実装
- Phase 7: テスト
- Phase 8: デプロイ

## 🐳 Docker での起動

```bash
# イメージビルド
docker build -t mydungeon-app .

# コンテナ起動
docker run -p 8000:8000 mydungeon-app
```

## 🌐 デプロイ (Render)

1. GitHubにリポジトリをプッシュ
2. [Render](https://render.com/) でアカウント作成
3. "New Web Service" を選択
4. リポジトリを接続
5. 自動デプロイ開始

### 無料プランの制約
- 15分間アクセスがないとスリープ
- 月750時間まで利用可能
- 512MBメモリ制限

## ⚙️ 設定

### 環境変数

`.env` ファイルを作成（`.env.example` を参考に）：

```
TARGET_URL=https://dungeon.humanjp.com/
HEADLESS=true
```

### CORS設定

`backend/config.py` で許可するオリジンを設定：

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://yourdomain.com"
]
```

## 🔧 トラブルシューティング

### スクレイピングが失敗する
- `backend/scraper.py` のセレクタを実際のサイト構造に合わせて修正
- ヘッドレスモードを無効化してデバッグ（`HEADLESS=false`）

### 日本語が文字化けする
- CSVファイルのエンコーディングを UTF-8 に設定
- 日本語フォントのインストール確認

### 画像が見つからない
- ファイル名と拡張子の一致を確認
- パス設定を確認

## 📝 開発状況

### 完了済み
- [x] プロジェクト構造設計
- [x] 開発手順書作成
- [x] スクレイピング機能実装（タイムゾーン対応、エラーハンドリング）
- [x] データ処理ロジック実装（CSV読み込み、必殺技判定）
- [x] レイアウト管理機能（色系統別ソート）
- [x] 画像処理実装（サイズ調整、色別配置、名前表示）
- [x] コア機能統合（DungeonServiceクラス）
- [x] 全機能の動作確認・テスト実行

### 次回開始
- [ ] バックエンドAPI構築（FastAPI）
- [ ] フロントエンド実装（HTML/CSS/JS）
- [ ] 統合テスト
- [ ] デプロイ準備

### テスト済みデータ
- ✅ 1991年9月16日13時50分（15アイテム、1必殺技）
- ✅ 1997年5月24日20時50分（19アイテム、7必殺技）
- ✅ 1991年4月22日11時00分（16アイテム、1必殺技）

## ⚠️ 注意事項

### スクレイピングについて
- 外部サイトの利用規約を確認してください
- robots.txt を尊重してください
- 過度なアクセスは避けてください
- レート制限を設けることを推奨します

### データについて
- `database/csv/` のCSVファイルは正しいエンコーディング（UTF-8）で保存してください
- 画像ファイルは適切なサイズに最適化してください

## 📞 サポート

問題が発生した場合は、以下を確認してください：
1. [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) のトラブルシューティングセクション
2. ログファイル（`backend/app.py` のログ出力）
3. ブラウザのコンソールエラー

## 📄 ライセンス

個人利用目的のプロジェクトです。

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**作成日**: 2025-11-24
**バージョン**: 1.0.0
