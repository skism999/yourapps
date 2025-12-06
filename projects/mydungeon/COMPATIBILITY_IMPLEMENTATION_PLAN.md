
# 相性診断機能 実装プラン

## 📋 概要

My Dungeonプロジェクトに2人の相性診断機能を追加します。1人診断とは別に、2人の生年月日時刻から相性を分析し、3種類の必殺技カテゴリ（二人で発動、あなた主導の相乗効果、相手主導の相乗効果）を表示します。

**実装方針**: 既存の1人診断コードに影響を与えず、新しいファイルを追加する形で実装

---

## 📁 ファイル構造

### 新規作成するファイル（5ファイル）

**Backend:**
- `backend/compatibility_processor.py` - 相性診断の必殺技カテゴリ分類ロジック
- `backend/compatibility_service.py` - 相性診断のサービス層（オーケストレーション）
- `backend/compatibility_image_processor.py` - 相性診断用の画像生成（3行レイアウト）

**Frontend:**
- `frontend/result_compatibility.html` - 相性診断結果ページ
- `frontend/js/compatibility.js` - 相性診断用JavaScript

### 変更するファイル（4ファイル）

**Backend:**
- `backend/models.py` - 相性診断用のデータモデルを追加
- `backend/app.py` - 新しいAPIエンドポイント `/api/generate-compatibility` を追加

**Frontend:**
- `frontend/index.html` - タブUI追加、相性診断フォーム追加
- `frontend/js/app.js` - タブ切り替えロジック、相性診断フォーム送信処理

---

## 🎯 実装順序（7ステップ）

### ステップ1: バックエンド - データモデル追加
### ステップ2: バックエンド - 相性プロセッサー
### ステップ3: バックエンド - 相性サービス
### ステップ4: バックエンド - 画像生成
### ステップ5: バックエンド - APIエンドポイント
### ステップ6: フロントエンド - タブUI
### ステップ7: フロントエンド - 相性診断結果ページ

詳細は `/home/codespace/.claude/plans/polished-exploring-pancake.md` を参照

---

## 🔍 重要な実装ポイント

### 必殺技カテゴリ分類ロジック

**3つのカテゴリ:**
1. **二人で発動する必殺技**: person1がAのみ、person2がBのみ（一人では片方しかない）
2. **person1の相乗効果**: person1がA+B、person2がAまたはB
3. **person2の相乗効果**: person2がA+B、person1がAまたはB

### 数字の色分け優先度
1. 紫（最優先）: joint_numbers
2. オレンジ: synergy_numbers
3. 赤: solo_hissatsu_numbers
4. グレー: その他

### 画像レイアウト
- ヘッダー: 「My Dungeon Result - 2人の必殺技 -」
- 3行の必殺技（色順序: 赤、桃、緑、黄緑、青、水、黄）
- 折り返し: 1行に4枚MAX

---

## ✅ 実装後の確認事項

- [ ] 1人診断が引き続き正常に動作する
- [ ] タブ切り替えがスムーズ
- [ ] 相性診断フォームから結果ページへ遷移
- [ ] 画像が3行レイアウトで表示（折り返し含む）
- [ ] 数字が紫/オレンジ/赤で色分けされる
- [ ] 3カテゴリの必殺技が正しく分類される
- [ ] モバイルで正常に表示・操作できる
- [ ] 画像・PDFダウンロードが動作する
