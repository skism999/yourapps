"""
My Dungeon FastAPI Application
生年月日と時刻から運命のアイテムと必殺技を診断するWebアプリケーション
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import os
import sys

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.dungeon_service import DungeonService

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    allow_origins=["*"],  # 開発環境では全て許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DungeonServiceのインスタンス
service = DungeonService()

# パス設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
OUTPUT_DIR = settings.OUTPUT_DIR
IMAGES_DIR = settings.IMAGES_DIR

# 静的ファイル配信
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# リクエストモデル
class GenerateRequest(BaseModel):
    birthdate: str  # YYYY-MM-DD
    birthtime: str  # HH:MM
    name: str = None  # オプション


@app.get("/")
async def root():
    """トップページ（入力画面）を返す"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "Welcome to My Dungeon API. Frontend not found."}


@app.post("/api/generate")
async def generate_result(request: GenerateRequest):
    """
    生年月日と時刻から診断結果を生成

    リクエスト:
        - birthdate: 生年月日 (YYYY-MM-DD形式)
        - birthtime: 時刻 (HH:MM形式)
        - name: 名前（オプション）

    レスポンス:
        - image_url: 生成された画像のURL
        - numbers: 取得した数字のリスト
        - hissatsu_numbers: 必殺技成立数字のリスト
        - items: アイテム情報のリスト
        - hissatsus: 必殺技情報のリスト
        - color_counts: 色ごとの枚数情報
        - actions: 動き方の説明
    """
    try:
        logger.info(f"Received request: {request.birthdate} {request.birthtime}, name={request.name}")

        # 結果生成
        result = await service.get_result_summary(
            request.birthdate,
            request.birthtime,
            request.name
        )

        # 画像URLを相対パスに変換
        image_filename = os.path.basename(result['image_path'])
        result['image_url'] = f"/output/{image_filename}"

        logger.info(f"Successfully generated result for {request.birthdate} {request.birthtime}")

        return result

    except Exception as e:
        logger.error(f"Error generating result: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "ok",
        "message": "My Dungeon API is running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
