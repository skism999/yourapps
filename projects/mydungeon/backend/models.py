from pydantic import BaseModel
from typing import List, Optional

class CalculateRequest(BaseModel):
    """生年月日と時刻のリクエスト"""
    birthdate: str  # "YYYY-MM-DD"
    birthtime: str  # "HH:MM"

class NumbersResponse(BaseModel):
    """取得した数字のレスポンス"""
    numbers: List[int]
    message: str

class ItemInfo(BaseModel):
    """アイテム情報"""
    no: int
    name: str
    pair_no: Optional[int] = None
    pair_name: Optional[str] = None
    hissatsu_no: Optional[int] = None
    hissatsu_name: Optional[str] = None
    color: str
    movement: str
    description: str
    on_state: str
    off_state: str
    image_path: str

class HissatsuInfo(BaseModel):
    """必殺技情報"""
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
    """最終結果のレスポンス"""
    items: List[ItemInfo]
    hissatsus: List[HissatsuInfo]
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None

class CompatibilityRequest(BaseModel):
    """相性診断のリクエスト"""
    person1_name: Optional[str] = None
    person1_birthdate: str  # "YYYY-MM-DD"
    person1_birthtime: str  # "HH:MM"
    person2_name: Optional[str] = None
    person2_birthdate: str  # "YYYY-MM-DD"
    person2_birthtime: str  # "HH:MM"
