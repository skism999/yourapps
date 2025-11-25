# マイダンジョン ブラウザアプリ 開発手順書

## 📋 プロジェクト概要

### 目的
生年月日と時刻を入力すると、外部サイト(dungeon.humanjp.com)から取得した数字に基づいて、対応するアイテム画像と情報を表示するWebアプリケーション

### 要件
- 生年月日・時刻入力フォーム
- 外部サイトのスクレイピング（15~25個の数字取得）
- データベース（CSV + 画像）からマッチング
- 結果を1枚の画像またはPDFで出力
- 必殺技の判定と表示
- シンプルでおしゃれなデザイン
- 他者もURL経由でアクセス可能

### 技術スタック
- **フロントエンド**: HTML, CSS (Tailwind), JavaScript
- **バックエンド**: Python (FastAPI), Playwright/Selenium
- **画像処理**: Pillow
- **データ処理**: pandas
- **PDF生成**: reportlab or weasyprint
- **デプロイ**: Render (無料枠)

---

## 🏗 プロジェクト構造

```
/workspaces/yourapps/projects/mydungeon/
├── backend/
│   ├── app.py                    # FastAPIメインアプリケーション
│   ├── scraper.py               # スクレイピング処理
│   ├── data_processor.py        # CSV処理とマッチングロジック
│   ├── image_processor.py       # 画像結合・PDF生成
│   ├── models.py                # データモデル定義
│   ├── config.py                # 設定ファイル
│   ├── requirements.txt         # Python依存パッケージ
│   └── .env.example            # 環境変数サンプル
├── frontend/
│   ├── index.html              # 入力画面
│   ├── result.html             # 結果表示画面
│   ├── css/
│   │   └── style.css          # カスタムスタイル
│   └── js/
│       └── app.js             # フロントエンドロジック
├── database/
│   ├── csv/
│   │   ├── item_list.csv
│   │   └── hissatsuwaza_list.csv
│   └── images/
│       ├── item/
│       └── Hissatsuwaza/
├── tests/
│   ├── test_scraper.py
│   ├── test_data_processor.py
│   └── test_image_processor.py
├── output/                      # 生成された画像・PDF保存先
├── Dockerfile
├── docker-compose.yml
├── render.yaml                 # Renderデプロイ設定
├── .gitignore
├── README.md
└── DEVELOPMENT_PLAN.md         # このファイル
```

---

## 📝 開発手順

### Phase 1: 環境構築 (推定時間: 30分)

#### 1.1 プロジェクト構造の作成

```bash
cd /workspaces/yourapps/projects/mydungeon

# ディレクトリ作成
mkdir -p backend frontend/css frontend/js tests output

# 必要なファイル作成
touch backend/app.py backend/scraper.py backend/data_processor.py backend/image_processor.py backend/models.py backend/config.py
touch backend/requirements.txt backend/.env.example
touch frontend/index.html frontend/result.html frontend/css/style.css frontend/js/app.js
touch tests/test_scraper.py tests/test_data_processor.py tests/test_image_processor.py
touch Dockerfile docker-compose.yml render.yaml .gitignore README.md
```

#### 1.2 requirements.txt の作成

**ファイル**: `backend/requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
playwright==1.40.0
pillow==10.1.0
pandas==2.1.3
python-dotenv==1.0.0
reportlab==4.0.7
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
```

#### 1.3 仮想環境のセットアップ

```bash
cd backend

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# パッケージインストール
pip install -r requirements.txt

# Playwrightブラウザインストール
playwright install chromium
```

#### 1.4 .gitignore の作成

**ファイル**: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# 環境変数
.env

# 出力ファイル
output/*.png
output/*.pdf

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

**チェックポイント**:
- [ ] ディレクトリ構造が正しく作成されている
- [ ] 仮想環境が有効化されている
- [ ] 必要なパッケージがインストールされている

---

### Phase 2: スクレイピング機能実装 (推定時間: 2-3時間)

#### 2.1 設定ファイルの作成

**ファイル**: `backend/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 外部サイト
    TARGET_URL = "https://dungeon.humanjp.com/"

    # ディレクトリパス
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    CSV_DIR = os.path.join(DATABASE_DIR, "csv")
    IMAGES_DIR = os.path.join(DATABASE_DIR, "images")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

    # CSVファイルパス
    ITEM_CSV = os.path.join(CSV_DIR, "item_list.csv")
    HISSATSU_CSV = os.path.join(CSV_DIR, "hissatsuwaza_list.csv")

    # 画像ディレクトリ
    ITEM_IMAGES_DIR = os.path.join(IMAGES_DIR, "item")
    HISSATSU_IMAGES_DIR = os.path.join(IMAGES_DIR, "Hissatsuwaza")

    # スクレイピング設定
    SCRAPING_TIMEOUT = 30000  # 30秒
    HEADLESS = True  # ヘッドレスモード

    # CORS設定
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"  # 本番環境のドメイン
    ]

settings = Settings()
```

**ファイル**: `backend/.env.example`

```
# 環境変数サンプル（本番環境では .env にコピーして使用）
TARGET_URL=https://dungeon.humanjp.com/
HEADLESS=true
```

#### 2.2 データモデルの定義

**ファイル**: `backend/models.py`

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

class CalculateRequest(BaseModel):
    birthdate: str  # "YYYY-MM-DD"
    birthtime: str  # "HH:MM"

class NumbersResponse(BaseModel):
    numbers: List[int]
    message: str

class ItemInfo(BaseModel):
    no: int
    name: str
    pair_no: Optional[int]
    pair_name: Optional[str]
    hissatsu_no: Optional[int]
    hissatsu_name: Optional[str]
    color: str
    movement: str
    description: str
    on_state: str
    off_state: str
    image_path: str

class HissatsuInfo(BaseModel):
    hissatsu_no: int
    name: str
    color: str
    meaning: str
    movement: str
    basic_posture: str
    talent: str
    characteristics: str
    advice: str
    on_state: str
    off_state: str
    image_path: str

class ResultResponse(BaseModel):
    items: List[ItemInfo]
    hissatsus: List[HissatsuInfo]
    image_url: Optional[str]
    pdf_url: Optional[str]
```

#### 2.3 スクレイピング機能の実装

**ファイル**: `backend/scraper.py`

```python
import asyncio
from playwright.async_api import async_playwright, Page
from typing import List
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DungeonScraper:
    """外部サイトからデータを取得するスクレイパー"""

    def __init__(self):
        self.url = settings.TARGET_URL
        self.timeout = settings.SCRAPING_TIMEOUT

    async def scrape_numbers(self, birthdate: str, birthtime: str) -> List[int]:
        """
        生年月日と時刻を入力して数字を取得

        Args:
            birthdate: 生年月日 (YYYY-MM-DD)
            birthtime: 時刻 (HH:MM)

        Returns:
            取得した数字のリスト
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.HEADLESS)
            page = await browser.new_page()

            try:
                logger.info(f"Accessing {self.url}")
                await page.goto(self.url, timeout=self.timeout)

                # TODO: 実際のサイト構造に合わせて以下を実装
                # 1. 生年月日入力フィールドを見つけて入力
                # await page.fill('#birthdate-selector', birthdate)

                # 2. 時刻入力フィールドを見つけて入力
                # await page.fill('#birthtime-selector', birthtime)

                # 3. 送信ボタンをクリック
                # await page.click('#submit-button')

                # 4. ポップアップまたは結果が表示されるまで待機
                # await page.wait_for_selector('#result-popup', timeout=self.timeout)

                # 5. 数字を抽出（表形式から）
                # numbers_elements = await page.query_selector_all('.number-cell')
                # numbers = []
                # for element in numbers_elements:
                #     text = await element.text_content()
                #     if text and text.isdigit():
                #         numbers.append(int(text))

                # 仮のデータ（開発用）
                numbers = [1, 8, 15, 22, 33]  # TODO: 実際のスクレイピングに置き換え

                logger.info(f"Extracted numbers: {numbers}")
                return numbers

            except Exception as e:
                logger.error(f"Scraping error: {str(e)}")
                raise
            finally:
                await browser.close()

# 使用例
async def main():
    scraper = DungeonScraper()
    numbers = await scraper.scrape_numbers("1990-01-01", "12:30")
    print(f"取得した数字: {numbers}")

if __name__ == "__main__":
    asyncio.run(main())
```

**⚠️ 重要**: 実際のサイト構造を確認して、セレクタを正しく設定する必要があります。

**チェックポイント**:
- [ ] Playwrightが正しくインストールされている
- [ ] スクレイピングテストが成功する（仮データでOK）
- [ ] エラーハンドリングが実装されている

---

### Phase 3: データ処理ロジック実装 (推定時間: 2時間)

#### 3.1 データプロセッサの実装

**ファイル**: `backend/data_processor.py`

```python
import pandas as pd
from typing import List, Dict, Tuple
from backend.config import settings
from backend.models import ItemInfo, HissatsuInfo
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """CSVデータの読み込みとマッチング処理"""

    def __init__(self):
        self.item_df = None
        self.hissatsu_df = None
        self.load_csv_data()

    def load_csv_data(self):
        """CSVファイルを読み込む"""
        try:
            # item_list.csvの読み込み
            self.item_df = pd.read_csv(
                settings.ITEM_CSV,
                encoding='utf-8',
                skiprows=1  # ヘッダーの矢印行をスキップ
            )
            logger.info(f"Loaded {len(self.item_df)} items from CSV")

            # hissatsuwaza_list.csvの読み込み
            self.hissatsu_df = pd.read_csv(
                settings.HISSATSU_CSV,
                encoding='utf-8',
                skiprows=1
            )
            logger.info(f"Loaded {len(self.hissatsu_df)} hissatsuwaza from CSV")

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    def get_items_by_numbers(self, numbers: List[int]) -> List[ItemInfo]:
        """
        数字リストから対応するアイテム情報を取得

        Args:
            numbers: スクレイピングで取得した数字のリスト

        Returns:
            アイテム情報のリスト
        """
        items = []
        for number in numbers:
            item_row = self.item_df[self.item_df['No'] == number]
            if not item_row.empty:
                item = item_row.iloc[0]

                # 画像パスを構築（拡張子を動的に検索）
                image_path = self._find_image_path(number, settings.ITEM_IMAGES_DIR)

                items.append(ItemInfo(
                    no=int(item['No']),
                    name=item['アイテム名'],
                    pair_no=int(item['対No']) if pd.notna(item['対No']) else None,
                    pair_name=item['対アイテム名'] if pd.notna(item['対アイテム名']) else None,
                    hissatsu_no=int(item['必殺No']) if pd.notna(item['必殺No']) else None,
                    hissatsu_name=item['必殺技名'] if pd.notna(item['必殺技名']) else None,
                    color=item['色'],
                    movement=item['動き方'],
                    description=item['説明'],
                    on_state=item['ON'],
                    off_state=item['OFF'],
                    image_path=image_path
                ))

        return items

    def detect_hissatsuwaza(self, numbers: List[int]) -> List[HissatsuInfo]:
        """
        必殺技の判定と情報取得

        Args:
            numbers: スクレイピングで取得した数字のリスト

        Returns:
            発動する必殺技情報のリスト
        """
        hissatsus = []
        activated_hissatsu_nos = set()

        # 数字をセットに変換（高速検索用）
        number_set = set(numbers)

        # 各数字について対Noとのペアをチェック
        for number in numbers:
            item_row = self.item_df[self.item_df['No'] == number]
            if not item_row.empty:
                item = item_row.iloc[0]
                pair_no = item['対No']
                hissatsu_no = item['必殺No']

                # 対Noが数字リストに含まれ、必殺Noが存在する場合
                if (pd.notna(pair_no) and
                    int(pair_no) in number_set and
                    pd.notna(hissatsu_no)):

                    hissatsu_no = int(hissatsu_no)

                    # 同じ必殺技を重複して追加しない
                    if hissatsu_no not in activated_hissatsu_nos:
                        activated_hissatsu_nos.add(hissatsu_no)

                        # 必殺技情報を取得
                        hissatsu_row = self.hissatsu_df[
                            self.hissatsu_df['必殺No'] == hissatsu_no
                        ]

                        if not hissatsu_row.empty:
                            h = hissatsu_row.iloc[0]
                            image_path = self._find_image_path(
                                hissatsu_no,
                                settings.HISSATSU_IMAGES_DIR,
                                suffix='_h'
                            )

                            hissatsus.append(HissatsuInfo(
                                hissatsu_no=hissatsu_no,
                                name=h['必殺技名'],
                                color=h['色'],
                                meaning=h['意味'],
                                movement=h['動き方'],
                                basic_posture=h['基本姿勢'],
                                talent=h['才能'],
                                characteristics=h['特性'],
                                advice=h['アドバイス'],
                                on_state=h['ON'],
                                off_state=h['OFF'],
                                image_path=image_path
                            ))

        logger.info(f"Detected {len(hissatsus)} hissatsuwaza")
        return hissatsus

    def _find_image_path(self, number: int, directory: str, suffix: str = '') -> str:
        """
        画像ファイルのパスを検索（拡張子を自動判定）

        Args:
            number: アイテムまたは必殺技のNo
            directory: 検索するディレクトリ
            suffix: ファイル名のサフィックス（例: '_h'）

        Returns:
            画像ファイルのパス
        """
        # 対応する拡張子リスト
        extensions = ['.jpg', '.jpeg', '.png', '.gif']

        for ext in extensions:
            filename = f"{number}{suffix}{ext}"
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                return filepath

        # 見つからない場合は警告を出して空文字を返す
        logger.warning(f"Image not found: {number}{suffix} in {directory}")
        return ""

# テスト用
if __name__ == "__main__":
    processor = DataProcessor()

    # テスト: 数字リストからアイテムを取得
    test_numbers = [1, 8, 15]
    items = processor.get_items_by_numbers(test_numbers)
    print(f"アイテム数: {len(items)}")
    for item in items:
        print(f"  - {item.name} (No.{item.no})")

    # テスト: 必殺技判定
    hissatsus = processor.detect_hissatsuwaza(test_numbers)
    print(f"\n必殺技数: {len(hissatsus)}")
    for h in hissatsus:
        print(f"  - {h.name} (No.{h.hissatsu_no})")
```

**チェックポイント**:
- [ ] CSVファイルが正しく読み込まれる
- [ ] アイテム検索が正しく動作する
- [ ] 必殺技判定ロジックが正しく動作する
- [ ] 画像パスが正しく取得できる

---

### Phase 4: 画像処理実装 (推定時間: 2-3時間)

#### 4.1 画像プロセッサの実装

**ファイル**: `backend/image_processor.py`

```python
from PIL import Image, ImageDraw, ImageFont
from typing import List
import os
from backend.config import settings
from backend.models import ItemInfo, HissatsuInfo
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """画像の結合とPDF生成"""

    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # デフォルトフォント（システムフォントまたはカスタムフォント）
        self.font_path = None  # TODO: 日本語フォントのパスを設定

    def create_result_image(
        self,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo]
    ) -> str:
        """
        アイテムと必殺技の画像を1枚に結合

        Args:
            items: アイテム情報のリスト
            hissatsu: 必殺技情報のリスト

        Returns:
            生成された画像のファイルパス
        """
        # 画像サイズ設定
        item_size = (200, 200)  # 各アイテム画像のサイズ
        grid_cols = 4  # 横に並べる数
        padding = 20
        info_height = 150  # 情報表示エリアの高さ

        # グリッド計算
        total_items = len(items) + len(hissatsus)
        grid_rows = (total_items + grid_cols - 1) // grid_cols

        # キャンバスサイズ
        canvas_width = grid_cols * (item_size[0] + padding) + padding
        canvas_height = grid_rows * (item_size[1] + info_height + padding) + padding

        # 新しい画像を作成（白背景）
        result_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(result_image)

        # フォント設定（サイズ調整）
        try:
            if self.font_path and os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, 14)
                font_title = ImageFont.truetype(self.font_path, 18)
            else:
                font = ImageFont.load_default()
                font_title = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            font_title = ImageFont.load_default()

        # アイテム画像を配置
        current_idx = 0
        for item in items:
            row = current_idx // grid_cols
            col = current_idx % grid_cols
            x = col * (item_size[0] + padding) + padding
            y = row * (item_size[1] + info_height + padding) + padding

            # アイテム画像を読み込んで配置
            if item.image_path and os.path.exists(item.image_path):
                try:
                    item_img = Image.open(item.image_path)
                    item_img = item_img.resize(item_size)
                    result_image.paste(item_img, (x, y))
                except Exception as e:
                    logger.error(f"Error loading image {item.image_path}: {e}")
                    # エラー時はグレーボックス
                    draw.rectangle([x, y, x + item_size[0], y + item_size[1]], fill='gray')

            # アイテム情報をテキストで追加
            text_y = y + item_size[1] + 10
            draw.text((x, text_y), f"No.{item.no}: {item.name}", fill='black', font=font_title)
            text_y += 25

            # 色と動き方
            draw.text((x, text_y), f"色: {item.color} | {item.movement}", fill='black', font=font)

            current_idx += 1

        # 必殺技画像を配置
        for hissatsu in hissatsus:
            row = current_idx // grid_cols
            col = current_idx % grid_cols
            x = col * (item_size[0] + padding) + padding
            y = row * (item_size[1] + info_height + padding) + padding

            # 必殺技画像を読み込んで配置
            if hissatsu.image_path and os.path.exists(hissatsu.image_path):
                try:
                    hissatsu_img = Image.open(hissatsu.image_path)
                    hissatsu_img = hissatsu_img.resize(item_size)
                    result_image.paste(hissatsu_img, (x, y))
                except Exception as e:
                    logger.error(f"Error loading image {hissatsu.image_path}: {e}")
                    draw.rectangle([x, y, x + item_size[0], y + item_size[1]], fill='darkgray')

            # 必殺技情報をテキストで追加
            text_y = y + item_size[1] + 10
            draw.text((x, text_y), f"必殺 No.{hissatsu.hissatsu_no}: {hissatsu.name}", fill='red', font=font_title)
            text_y += 25
            draw.text((x, text_y), f"{hissatsu.meaning}", fill='black', font=font)

            current_idx += 1

        # ファイル名生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"result_{timestamp}.png")
        result_image.save(output_path)

        logger.info(f"Result image saved: {output_path}")
        return output_path

    def create_pdf(
        self,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo],
        image_path: str = None
    ) -> str:
        """
        PDF形式で結果を出力

        Args:
            items: アイテム情報のリスト
            hissatsus: 必殺技情報のリスト
            image_path: 既に生成された画像のパス（オプション）

        Returns:
            生成されたPDFのファイルパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"result_{timestamp}.pdf")

        # PDFキャンバス作成
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # タイトル
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "My Dungeon Result")

        y_position = height - 100

        # 画像が提供されている場合は埋め込み
        if image_path and os.path.exists(image_path):
            try:
                img = ImageReader(image_path)
                c.drawImage(img, 50, y_position - 400, width=500, height=400, preserveAspectRatio=True)
                y_position -= 450
            except Exception as e:
                logger.error(f"Error embedding image in PDF: {e}")

        # アイテム情報を追加（改ページ）
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Item Details")

        y_position = height - 100
        c.setFont("Helvetica", 10)

        for item in items:
            if y_position < 100:  # ページ下部に達したら改ページ
                c.showPage()
                y_position = height - 50

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"No.{item.no}: {item.name}")
            y_position -= 20

            c.setFont("Helvetica", 10)
            c.drawString(70, y_position, f"Color: {item.color} | Movement: {item.movement}")
            y_position -= 15

            # 説明（長い場合は複数行に分割）
            description_lines = self._wrap_text(item.description, 80)
            for line in description_lines:
                c.drawString(70, y_position, line)
                y_position -= 15

            y_position -= 10

        # 必殺技情報を追加
        if hissatsus:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Hissatsuwaza Details")

            y_position = height - 100

            for h in hissatsus:
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50

                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, f"No.{h.hissatsu_no}: {h.name}")
                y_position -= 20

                c.setFont("Helvetica", 10)
                c.drawString(70, y_position, f"Meaning: {h.meaning}")
                y_position -= 15

                talent_lines = self._wrap_text(h.talent, 80)
                for line in talent_lines:
                    c.drawString(70, y_position, line)
                    y_position -= 15

                y_position -= 10

        c.save()
        logger.info(f"PDF saved: {output_path}")
        return output_path

    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """テキストを指定文字数で折り返し"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines

# テスト用
if __name__ == "__main__":
    from backend.data_processor import DataProcessor

    processor = DataProcessor()
    numbers = [1, 8, 15]
    items = processor.get_items_by_numbers(numbers)
    hissatsus = processor.detect_hissatsuwaza(numbers)

    img_processor = ImageProcessor()
    image_path = img_processor.create_result_image(items, hissatsus)
    print(f"画像生成完了: {image_path}")

    pdf_path = img_processor.create_pdf(items, hissatsus, image_path)
    print(f"PDF生成完了: {pdf_path}")
```

**チェックポイント**:
- [ ] 画像が正しく読み込まれる
- [ ] 画像が正しく結合される
- [ ] PDFが正しく生成される
- [ ] 日本語テキストが正しく表示される（フォント設定要確認）

---

### Phase 5: FastAPIバックエンド構築 (推定時間: 2時間)

#### 5.1 メインアプリケーション

**ファイル**: `backend/app.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from backend.config import settings
from backend.models import CalculateRequest, NumbersResponse, ResultResponse
from backend.scraper import DungeonScraper
from backend.data_processor import DataProcessor
from backend.image_processor import ImageProcessor
import os

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(
    title="My Dungeon API",
    description="生年月日から運命のアイテムと必殺技を診断",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信（フロントエンド）
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 出力ファイル配信
app.mount("/output", StaticFiles(directory=settings.OUTPUT_DIR), name="output")

# プロセッサのインスタンス化（起動時に1回だけ）
scraper = DungeonScraper()
data_processor = DataProcessor()
image_processor = ImageProcessor()

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.post("/api/calculate", response_model=NumbersResponse)
async def calculate_numbers(request: CalculateRequest):
    """
    生年月日と時刻から数字を取得
    """
    try:
        logger.info(f"Calculate request: {request.birthdate} {request.birthtime}")

        # スクレイピング実行
        numbers = await scraper.scrape_numbers(request.birthdate, request.birthtime)

        if not numbers:
            raise HTTPException(status_code=404, detail="数字の取得に失敗しました")

        return NumbersResponse(
            numbers=numbers,
            message=f"{len(numbers)}個の数字を取得しました"
        )

    except Exception as e:
        logger.error(f"Calculate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-result", response_model=ResultResponse)
async def generate_result(numbers_response: NumbersResponse):
    """
    数字リストから結果（画像・PDF）を生成
    """
    try:
        numbers = numbers_response.numbers
        logger.info(f"Generating result for numbers: {numbers}")

        # アイテム情報取得
        items = data_processor.get_items_by_numbers(numbers)

        # 必殺技判定
        hissatsus = data_processor.detect_hissatsuwaza(numbers)

        # 画像生成
        image_path = image_processor.create_result_image(items, hissatsus)
        image_filename = os.path.basename(image_path)

        # PDF生成
        pdf_path = image_processor.create_pdf(items, hissatsus, image_path)
        pdf_filename = os.path.basename(pdf_path)

        return ResultResponse(
            items=items,
            hissatsus=hissatsus,
            image_url=f"/output/{image_filename}",
            pdf_url=f"/output/{pdf_filename}"
        )

    except Exception as e:
        logger.error(f"Generate result error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**起動方法**:

```bash
cd /workspaces/yourapps/projects/mydungeon

# 開発サーバー起動
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**チェックポイント**:
- [ ] サーバーが正常に起動する
- [ ] `/api/health` エンドポイントが応答する
- [ ] CORS設定が正しい
- [ ] 静的ファイルが配信される

---

### Phase 6: フロントエンド実装 (推定時間: 3時間)

#### 6.1 入力画面

**ファイル**: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Dungeon - 運命の診断</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body class="bg-gradient-to-br from-purple-100 to-blue-100 min-h-screen">
    <div class="container mx-auto px-4 py-16">
        <div class="max-w-md mx-auto bg-white rounded-2xl shadow-2xl p-8">
            <!-- ヘッダー -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-purple-600 mb-2">My Dungeon</h1>
                <p class="text-gray-600">あなたの運命のアイテムを診断</p>
            </div>

            <!-- フォーム -->
            <form id="input-form" class="space-y-6">
                <!-- 生年月日入力 -->
                <div>
                    <label for="birthdate" class="block text-sm font-medium text-gray-700 mb-2">
                        生年月日
                    </label>
                    <input
                        type="date"
                        id="birthdate"
                        name="birthdate"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                    >
                </div>

                <!-- 時刻入力 -->
                <div>
                    <label for="birthtime" class="block text-sm font-medium text-gray-700 mb-2">
                        出生時刻
                    </label>
                    <input
                        type="time"
                        id="birthtime"
                        name="birthtime"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                    >
                </div>

                <!-- 送信ボタン -->
                <button
                    type="submit"
                    id="submit-btn"
                    class="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-bold py-3 px-6 rounded-lg hover:from-purple-600 hover:to-blue-600 transform hover:scale-105 transition duration-200 shadow-lg"
                >
                    診断する
                </button>
            </form>

            <!-- ローディング表示 -->
            <div id="loading" class="hidden mt-6 text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
                <p class="mt-4 text-gray-600">診断中...</p>
            </div>

            <!-- エラー表示 -->
            <div id="error-message" class="hidden mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            </div>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
```

#### 6.2 結果表示画面

**ファイル**: `frontend/result.html`

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>診断結果 - My Dungeon</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body class="bg-gradient-to-br from-purple-100 to-blue-100 min-h-screen">
    <div class="container mx-auto px-4 py-16">
        <!-- ヘッダー -->
        <div class="text-center mb-12">
            <h1 class="text-4xl font-bold text-purple-600 mb-2">診断結果</h1>
            <p class="text-gray-600">あなたの運命のアイテムと必殺技</p>
        </div>

        <!-- 結果画像 -->
        <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <div id="result-image-container" class="text-center">
                <img id="result-image" src="" alt="診断結果" class="mx-auto rounded-lg shadow-lg">
            </div>
        </div>

        <!-- ダウンロードボタン -->
        <div class="max-w-4xl mx-auto flex justify-center space-x-4 mb-8">
            <a
                id="download-image-btn"
                href="#"
                download
                class="bg-blue-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-600 transform hover:scale-105 transition duration-200 shadow-lg"
            >
                画像をダウンロード
            </a>
            <a
                id="download-pdf-btn"
                href="#"
                download
                class="bg-green-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-600 transform hover:scale-105 transition duration-200 shadow-lg"
            >
                PDFをダウンロード
            </a>
        </div>

        <!-- アイテム詳細 -->
        <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">アイテム詳細</h2>
            <div id="items-container" class="space-y-6">
                <!-- JavaScriptで動的に生成 -->
            </div>
        </div>

        <!-- 必殺技詳細 -->
        <div id="hissatsuwaza-section" class="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8 mb-8 hidden">
            <h2 class="text-2xl font-bold text-red-600 mb-6">発動した必殺技</h2>
            <div id="hissatsuwaza-container" class="space-y-6">
                <!-- JavaScriptで動的に生成 -->
            </div>
        </div>

        <!-- トップに戻るボタン -->
        <div class="text-center">
            <a
                href="/"
                class="inline-block bg-gray-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-600 transform hover:scale-105 transition duration-200 shadow-lg"
            >
                最初に戻る
            </a>
        </div>

        <!-- ローディング -->
        <div id="loading" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-white p-8 rounded-lg text-center">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto"></div>
                <p class="mt-4 text-gray-600">結果を生成中...</p>
            </div>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
    <script>
        // ページロード時に結果を表示
        window.addEventListener('DOMContentLoaded', displayResult);
    </script>
</body>
</html>
```

#### 6.3 JavaScript

**ファイル**: `frontend/js/app.js`

```javascript
// API base URL
const API_BASE = '';  // 同じオリジンの場合は空文字

// 入力フォームの処理
document.getElementById('input-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const birthdate = document.getElementById('birthdate').value;
    const birthtime = document.getElementById('birthtime').value;

    // ローディング表示
    showLoading();
    hideError();

    try {
        // Step 1: 数字を取得
        const numbersResponse = await fetch(`${API_BASE}/api/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                birthdate: birthdate,
                birthtime: birthtime
            })
        });

        if (!numbersResponse.ok) {
            throw new Error('数字の取得に失敗しました');
        }

        const numbersData = await numbersResponse.json();
        console.log('取得した数字:', numbersData.numbers);

        // Step 2: 結果を生成
        const resultResponse = await fetch(`${API_BASE}/api/generate-result`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(numbersData)
        });

        if (!resultResponse.ok) {
            throw new Error('結果の生成に失敗しました');
        }

        const resultData = await resultResponse.json();

        // 結果をセッションストレージに保存
        sessionStorage.setItem('result', JSON.stringify(resultData));

        // 結果ページに遷移
        window.location.href = '/static/result.html';

    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
});

// 結果表示処理
function displayResult() {
    const resultData = JSON.parse(sessionStorage.getItem('result'));

    if (!resultData) {
        console.error('結果データが見つかりません');
        window.location.href = '/';
        return;
    }

    // 画像表示
    const resultImage = document.getElementById('result-image');
    if (resultImage && resultData.image_url) {
        resultImage.src = resultData.image_url;
    }

    // ダウンロードリンク設定
    const downloadImageBtn = document.getElementById('download-image-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');

    if (downloadImageBtn && resultData.image_url) {
        downloadImageBtn.href = resultData.image_url;
    }

    if (downloadPdfBtn && resultData.pdf_url) {
        downloadPdfBtn.href = resultData.pdf_url;
    }

    // アイテム詳細を表示
    const itemsContainer = document.getElementById('items-container');
    if (itemsContainer) {
        itemsContainer.innerHTML = resultData.items.map(item => `
            <div class="border-l-4 border-${getColorClass(item.color)} pl-4 py-2">
                <h3 class="text-xl font-bold text-gray-800">No.${item.no}: ${item.name}</h3>
                <p class="text-sm text-gray-600 mb-2">色: ${item.color} | ${item.movement}</p>
                <p class="text-gray-700">${item.description}</p>
                <div class="mt-2 text-sm">
                    <p class="text-green-600"><strong>ON:</strong> ${item.on_state}</p>
                    <p class="text-red-600"><strong>OFF:</strong> ${item.off_state}</p>
                </div>
            </div>
        `).join('');
    }

    // 必殺技詳細を表示
    if (resultData.hissatsus && resultData.hissatsus.length > 0) {
        const hissatsuSection = document.getElementById('hissatsuwaza-section');
        const hissatsuContainer = document.getElementById('hissatsuwaza-container');

        if (hissatsuSection && hissatsuContainer) {
            hissatsuSection.classList.remove('hidden');
            hissatsuContainer.innerHTML = resultData.hissatsus.map(h => `
                <div class="border-l-4 border-red-500 pl-4 py-2 bg-red-50">
                    <h3 class="text-xl font-bold text-red-600">必殺No.${h.hissatsu_no}: ${h.name}</h3>
                    <p class="text-sm text-gray-600 mb-2">${h.meaning}</p>
                    <p class="text-gray-700 mb-2"><strong>才能:</strong> ${h.talent}</p>
                    <p class="text-gray-700 mb-2"><strong>特性:</strong> ${h.characteristics}</p>
                    <p class="text-blue-600"><strong>アドバイス:</strong> ${h.advice}</p>
                </div>
            `).join('');
        }
    }
}

// ユーティリティ関数
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.classList.remove('hidden');
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) errorDiv.classList.add('hidden');
}

function getColorClass(color) {
    const colorMap = {
        '赤': 'red-500',
        '青': 'blue-500',
        '黄': 'yellow-500',
        '緑': 'green-500',
        '紫': 'purple-500',
        '桃': 'pink-500',
        '黄緑': 'lime-500',
        '水': 'cyan-500'
    };
    return colorMap[color] || 'gray-500';
}
```

#### 6.4 カスタムCSS

**ファイル**: `frontend/css/style.css`

```css
/* カスタムスタイル */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
}

/* アニメーション */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.container > div {
    animation: fadeIn 0.6s ease-out;
}

/* ボタンホバーエフェクト */
button, a {
    cursor: pointer;
    user-select: none;
}

/* スクロールバーカスタマイズ */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* レスポンシブ画像 */
#result-image {
    max-width: 100%;
    height: auto;
}
```

**チェックポイント**:
- [ ] 入力フォームが正しく動作する
- [ ] APIと通信できる
- [ ] 結果ページが正しく表示される
- [ ] ダウンロードボタンが動作する
- [ ] レスポンシブデザインが機能する

---

### Phase 7: テスト (推定時間: 1-2時間)

#### 7.1 単体テストの作成

**ファイル**: `tests/test_data_processor.py`

```python
import pytest
from backend.data_processor import DataProcessor

def test_load_csv():
    processor = DataProcessor()
    assert processor.item_df is not None
    assert len(processor.item_df) > 0

def test_get_items_by_numbers():
    processor = DataProcessor()
    numbers = [1, 8]
    items = processor.get_items_by_numbers(numbers)
    assert len(items) == 2
    assert items[0].no == 1
    assert items[1].no == 8

def test_detect_hissatsuwaza():
    processor = DataProcessor()
    # No.1とNo.8のペアは必殺No.1を発動
    numbers = [1, 8]
    hissatsus = processor.detect_hissatsuwaza(numbers)
    assert len(hissatsus) > 0
```

#### 7.2 統合テストの実施

```bash
# pytestのインストール
pip install pytest pytest-asyncio

# テスト実行
pytest tests/ -v
```

**手動テスト項目**:
- [ ] 生年月日・時刻入力が正しく動作する
- [ ] スクレイピングが成功する
- [ ] 数字が正しく取得される
- [ ] アイテムが正しく表示される
- [ ] 必殺技判定が正しい
- [ ] 画像が正しく生成される
- [ ] PDFが正しく生成される
- [ ] ダウンロードが正しく動作する

---

### Phase 8: デプロイ (推定時間: 2時間)

#### 8.1 Dockerfile の作成

**ファイル**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwrightブラウザのインストール
RUN playwright install chromium
RUN playwright install-deps chromium

# アプリケーションファイルのコピー
COPY . .

# ポート公開
EXPOSE 8000

# 起動コマンド
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.2 Render設定

**ファイル**: `render.yaml`

```yaml
services:
  - type: web
    name: mydungeon-app
    env: docker
    plan: free
    region: oregon
    buildCommand: "echo 'Building...'"
    startCommand: "uvicorn backend.app:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: HEADLESS
        value: true
```

#### 8.3 デプロイ手順

1. **Gitリポジトリの作成**

```bash
cd /workspaces/yourapps/projects/mydungeon
git init
git add .
git commit -m "Initial commit"
```

2. **GitHubにプッシュ**

```bash
# GitHubでリポジトリ作成後
git remote add origin https://github.com/yourusername/mydungeon.git
git push -u origin main
```

3. **Renderでデプロイ**
   - Render.com にアクセス
   - "New Web Service" を選択
   - GitHubリポジトリを接続
   - `render.yaml` が自動検出される
   - "Create Web Service" をクリック

4. **環境変数の設定**
   - Renderダッシュボードで環境変数を設定
   - 必要に応じてシークレットを追加

**チェックポイント**:
- [ ] Dockerイメージがビルドできる
- [ ] Renderにデプロイ成功
- [ ] アプリケーションが正常に動作する
- [ ] 外部からアクセスできる

---

## 🔧 トラブルシューティング

### よくある問題と解決策

1. **スクレイピングが失敗する**
   - ヘッドレスモードを無効化して動作確認
   - セレクタが正しいか確認
   - タイムアウト時間を延長

2. **日本語が文字化けする**
   - CSVファイルのエンコーディングを確認
   - フォント設定を確認
   - UTF-8で保存されているか確認

3. **画像が見つからない**
   - ファイル名と拡張子が一致しているか確認
   - パスが正しいか確認

4. **メモリ不足エラー**
   - Renderの無料プランは512MBメモリ制限
   - 画像サイズを削減
   - 有料プランにアップグレード

---

## 📚 次のステップ

- [ ] スクレイピング部分を実際のサイト構造に合わせて実装
- [ ] 日本語フォントの設定
- [ ] エラーハンドリングの強化
- [ ] キャッシュ機能の追加
- [ ] ログ機能の強化
- [ ] 管理画面の追加（オプション）
- [ ] ユーザー認証（オプション）

---

## 📞 参考リンク

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Playwright公式ドキュメント](https://playwright.dev/python/)
- [Render公式ドキュメント](https://render.com/docs)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 📊 実装進捗状況

### ✅ 完了したフェーズ

#### Phase 1: 環境構築 (完了)
- プロジェクト構造作成
- 必要なパッケージのインストール（Playwright, Pillow, pandas, pydantic）
- .env設定（HEADLESS=true）

#### Phase 2: スクレイピング機能 (完了)
- `backend/scraper.py` 実装
- タイムゾーン設定（Asia/Tokyo）
- 数字の正確な抽出（15-25個）
- テスト実装（`tests/test_scraper.py`）

#### Phase 3: データ処理ロジック (完了)
- `backend/models.py` - データモデル定義
- `backend/data_processor.py` - CSV読み込みとマッチング
- 必殺技判定ロジック（ペアアイテム検出）
- `backend/layout_manager.py` - 色系統別ソート機能
- テスト実装（`tests/test_data_processor.py`, `tests/test_integration.py`）

#### Phase 4: 画像結合機能 (完了)
- `backend/image_processor.py` 実装
- **画像サイズ調整**:
  - アイテム画像: 横幅188px (元の75%)
  - 必殺技画像: 横幅376px (アイテムの2倍)
  - 高さ: 250px統一
- **レイアウト機能**:
  - 色系統別配置（赤系→緑系→青系→黄系）
  - 色ごとに細分化（例：青→水）
  - 必殺技は各色系統の最左に配置
  - 色が変わる時だけ隙間を追加（30px）
  - 行間: 40px
- **ヘッダー機能**:
  - タイトル表示
  - 名前入力・表示機能
  - 生年月日・時刻表示
- テスト実装（`tests/test_image_processor.py`）

#### Phase 4.5: コア機能の統合 (完了)
- `backend/dungeon_service.py` 作成
- スクレイピング→データ処理→画像生成の完全なフローを1つのサービスクラスに統合
- `get_result_summary()` メソッドでJSON形式の結果を提供

**テスト実行結果**:
- ✅ 1991年9月16日13時50分: 15アイテム、1必殺技
- ✅ 1997年5月24日20時50分: 19アイテム、7必殺技
- ✅ 1991年4月22日11時00分: 16アイテム、1必殺技
- すべて正常に動作確認済み

### 🚧 次回開始ポイント: Phase 5

**Phase 5: FastAPIバックエンド構築**

次回は以下から開始します：

1. **FastAPIアプリケーション作成** (`backend/app.py`)
   - `/api/generate` エンドポイント（POST）
   - リクエスト: `{ birthdate, birthtime, name }`
   - レスポンス: サマリー情報 + 画像URL
   - 静的ファイル配信設定
   - CORS設定

2. **準備済みのコンポーネント**:
   - ✅ `DungeonService` クラス（完全なビジネスロジック）
   - ✅ すべてのバックエンド機能が動作確認済み
   - ✅ テストデータで検証済み

3. **必要な追加パッケージ**:
   ```bash
   pip install fastapi uvicorn
   ```

4. **実装予定のエンドポイント**:
   - `GET /` - トップページ（HTML）
   - `POST /api/generate` - 結果生成API
   - `GET /output/{filename}` - 生成画像の配信
   - `GET /health` - ヘルスチェック

**次回の作業フロー**:
1. FastAPIアプリケーション作成
2. フロントエンドHTML/CSS/JS作成
3. ローカルテスト実行
4. 統合テスト

---

**最終更新日**: 2025-11-24
**作成者**: Claude Code
