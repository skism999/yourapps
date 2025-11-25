import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 外部サイト
    TARGET_URL = os.getenv("TARGET_URL", "https://dungeon.humanjp.com/")

    # ディレクトリパス
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    CSV_DIR = os.path.join(DATABASE_DIR, "csv")
    IMAGES_DIR = os.path.join(DATABASE_DIR, "images")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

    # CSVファイルパス
    ITEM_CSV = os.path.join(CSV_DIR, "item_list.csv")
    HISSATSU_CSV = os.path.join(CSV_DIR, "hissatsuwaza_list.csv")
    COLOR_MEANING_CSV = os.path.join(CSV_DIR, "meaning_of_color.csv")
    ACTION_CSV = os.path.join(CSV_DIR, "how_to_action.csv")

    # 画像ディレクトリ
    ITEM_IMAGES_DIR = os.path.join(IMAGES_DIR, "item")
    HISSATSU_IMAGES_DIR = os.path.join(IMAGES_DIR, "Hissatsuwaza")

    # スクレイピング設定
    SCRAPING_TIMEOUT = 30000  # 30秒
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

    # CORS設定
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"
    ]

settings = Settings()
