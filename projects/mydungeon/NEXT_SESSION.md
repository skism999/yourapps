# 次回セッション用メモ

**作成日**: 2025年12月4日
**ブランチ**: action_2
**状態**: 相性診断機能の実装完了、動作確認待ち

---

## 📌 現在の状況

相性診断機能（2人診断）のコーディングは**すべて完了**しました。
次回は動作確認とデバッグを行います。

### 実装完了内容

✅ **バックエンド**（5ファイル）:
- `backend/models.py` - CompatibilityRequestモデル追加
- `backend/compatibility_processor.py` - 3カテゴリ必殺技分類ロジック（新規作成）
- `backend/compatibility_service.py` - 相性診断サービス（新規作成）
- `backend/compatibility_image_processor.py` - 3行レイアウト画像生成（新規作成）
- `backend/app.py` - `/api/generate-compatibility`エンドポイント追加

✅ **フロントエンド**（4ファイル）:
- `frontend/index.html` - タブUI追加、相性診断フォーム追加
- `frontend/js/app.js` - タブ切り替え、相性フォーム送信処理
- `frontend/result_compatibility.html` - 相性結果ページ（新規作成）
- `frontend/js/compatibility.js` - 相性結果表示JS（新規作成）

✅ **バグ修正**:
- `compatibility_processor.py`の`_find_hissatsu_image_path`を`_find_image_path`に修正
- `settings`インポート追加

---

## 🔄 次回セッションでやること

### 1. Dockerコンテナの再起動

```bash
cd /workspaces/yourapps/projects/mydungeon
docker-compose restart mydungeon
```

### 2. ブラウザのキャッシュクリア

- 方法1: ブラウザでスーパーリロード（Ctrl+Shift+R または Cmd+Shift+R）
- 方法2: ブラウザの開発者ツール > Network > Disable cache

### 3. 動作確認

#### 3-1. タブ切り替え確認
1. `http://localhost:8000` にアクセス
2. 「1人診断」タブと「相性診断」タブが表示されることを確認
3. タブをクリックして切り替えできることを確認
4. 「相性診断」タブをクリックすると、2人分のフォームが表示されることを確認

#### 3-2. 相性診断の実行
1. 「相性診断」タブを選択
2. **あなたの情報**:
   - 名前: テスト太郎（任意）
   - 生年月日: 1991年9月16日
   - 出生時刻: 13時50分
3. **相手の情報**:
   - 名前: テスト花子（任意）
   - 生年月日: 1997年5月24日
   - 出生時刻: 20時50分
4. 「相性診断する」ボタンをクリック
5. ローディング表示が出ることを確認
6. 結果ページ（`result_compatibility.html`）に遷移することを確認

#### 3-3. 結果ページの確認
1. 相性画像が表示されることを確認（3行レイアウト）
2. **あなたの数字**セクション:
   - 数字が色分けされている（紫/オレンジ/赤/グレー）
3. **相手の数字**セクション:
   - 数字が色分けされている（紫/オレンジ/赤/グレー）
4. **3つの必殺技カテゴリ**が表示される:
   - 二人で発動する必殺技
   - あなただけで発動するが相手がいて相乗効果がある必殺技
   - 相手だけで発動するがあなたがいて相乗効果がある必殺技
5. 色ごとの枚数、動き方の説明が表示される
6. 「画像をダウンロード」ボタンと「詳細をPDFで保存」ボタンが動作する

---

## 🐛 エラーが出た場合の対処

### ケース1: タブが表示されない / 切り替えできない

**確認方法**:
```bash
# ブラウザの開発者ツール（F12） > Console でエラー確認
```

**考えられる原因**:
- JavaScriptのキャッシュが残っている → スーパーリロード
- `app.js`の読み込みエラー → バージョン番号が`?v=5`か確認

**対処**:
```bash
# index.htmlの318行目を確認
cat /workspaces/yourapps/projects/mydungeon/frontend/index.html | grep "app.js"
# 出力: <script src="/static/js/app.js?v=5"></script>
```

### ケース2: 相性診断フォームが表示されない

**確認方法**:
```bash
# index.htmlの185-309行目を確認
cat -n /workspaces/yourapps/projects/mydungeon/frontend/index.html | sed -n '185,309p'
```

**考えられる原因**:
- HTMLの記述ミス
- CSSの`hidden`クラスが適用されたまま

### ケース3: APIエラー（500 Internal Server Error）

**確認方法**:
```bash
# バックエンドログを確認
docker-compose logs -f mydungeon
```

**考えられる原因**:
- Pythonのインポートエラー
- CSVデータの読み込みエラー
- 画像パスの問題

**対処**:
```bash
# コンテナ内でPythonエラーを確認
docker-compose exec mydungeon python -c "from backend.compatibility_service import CompatibilityService"
```

### ケース4: 画像生成エラー

**確認方法**:
```bash
# outputディレクトリを確認
ls -la /workspaces/yourapps/projects/mydungeon/output/
```

**考えられる原因**:
- 必殺技画像が見つからない
- Pillowライブラリのエラー

---

## 📋 テストチェックリスト

次回セッションで以下をチェック:

- [ ] Dockerコンテナ再起動完了
- [ ] ブラウザキャッシュクリア完了
- [ ] タブUIが表示される
- [ ] タブ切り替えが動作する
- [ ] 相性診断フォームが表示される
- [ ] フォーム送信が成功する
- [ ] APIが正しくレスポンスを返す
- [ ] 結果ページに遷移する
- [ ] 相性画像が表示される（3行レイアウト）
- [ ] 数字が色分けされている（紫/オレンジ/赤/グレー）
- [ ] 3カテゴリの必殺技が表示される
- [ ] 色ごとの枚数が表示される
- [ ] 動き方の説明が表示される
- [ ] 画像ダウンロードが動作する
- [ ] PDFダウンロードが動作する

すべてチェック完了後 → mainブランチにマージ → ConoHa VPSデプロイ

---

## 🔍 重要な技術詳細

### 必殺技カテゴリ分類ロジック

**二人で発動する必殺技**:
- person1がAのみ、person2がBのみ持っている（一人では片方のみ）
- 例: person1=[1,3,5], person2=[2,4,6] で (1,2) がペア → joint

**Person1の相乗効果**:
- person1がA+B（両方）、person2がAまたはB（片方）
- person1が単独で発動できるが、person2がいることで相乗効果

**Person2の相乗効果**:
- person2がA+B（両方）、person1がAまたはB（片方）
- person2が単独で発動できるが、person1がいることで相乗効果

### 数字の色分け優先度

1. **紫（最優先）**: joint_numbers（二人で発動）
2. **オレンジ**: synergy_numbers（相乗効果）
3. **赤**: solo_hissatsu_numbers（単独必殺技）
4. **グレー**: その他

### 画像レイアウト

- **3行構成**:
  - 行1: 二人で発動する必殺技
  - 行2: あなたの相乗効果必殺技
  - 行3: 相手の相乗効果必殺技
- **色順序**: 赤 → 桃 → 緑 → 黄緑 → 青 → 水 → 黄
- **折り返し**: 最大4枚/行、5枚目から次の行へ

---

## 📂 変更されたファイル一覧

### 新規作成（5ファイル）
```
backend/compatibility_processor.py
backend/compatibility_service.py
backend/compatibility_image_processor.py
frontend/result_compatibility.html
frontend/js/compatibility.js
```

### 変更（4ファイル）
```
backend/models.py           - CompatibilityRequest追加
backend/app.py              - /api/generate-compatibility追加
frontend/index.html         - タブUI追加、?v=5
frontend/js/app.js          - タブ切り替え、相性フォーム送信
```

### 修正（1ファイル）
```
backend/compatibility_processor.py - _find_image_path修正、settings追加
```

---

## 💡 Claude への指示（次回セッション開始時）

次回セッション開始時に以下を伝えてください:

```
「相性診断機能の実装が完了しています。
NEXT_SESSION.mdを確認して、動作確認とデバッグを行ってください。
ブランチはaction_2です。」
```

または:

```
「NEXT_SESSION.mdを読んで、次の作業を続けてください。」
```

---

## 🎯 最終ゴール

1. ✅ 相性診断機能の実装完了（コーディング完了）
2. 🔄 動作確認とデバッグ ← **次回ここから**
3. ⬜ mainブランチにマージ
4. ⬜ ConoHa VPSにデプロイ
5. ⬜ 本番環境で動作確認

---

**重要**: 既存の1人診断機能には一切影響しないように実装されています。
