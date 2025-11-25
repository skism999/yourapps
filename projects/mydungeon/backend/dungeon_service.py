"""
My Dungeonサービス
スクレイピングから画像生成までの完全なフローを提供
"""
import logging
from typing import Tuple, List
from backend.scraper import DungeonScraper
from backend.data_processor import DataProcessor
from backend.image_processor import ImageProcessor
from backend.models import ItemInfo, HissatsuInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DungeonService:
    """My Dungeonの完全なサービス"""

    def __init__(self):
        self.scraper = DungeonScraper()
        self.data_processor = DataProcessor()
        self.image_processor = ImageProcessor()

    async def generate_dungeon_result(
        self,
        birthdate: str,
        birthtime: str,
        name: str = None
    ) -> Tuple[str, List[int], List[ItemInfo], List[HissatsuInfo]]:
        """
        生年月日と時刻から完全な結果を生成

        Args:
            birthdate: 生年月日 (YYYY-MM-DD形式)
            birthtime: 時刻 (HH:MM形式)
            name: 名前（オプション）

        Returns:
            (画像パス, 数字リスト, アイテムリスト, 必殺技リスト)
        """
        logger.info(f"Starting dungeon result generation for {birthdate} {birthtime}")

        # Step 1: スクレイピング
        logger.info("Step 1: Scraping numbers...")
        numbers = await self.scraper.scrape_numbers(birthdate, birthtime)
        logger.info(f"Scraped {len(numbers)} numbers: {numbers}")

        # Step 2: アイテム情報取得
        logger.info("Step 2: Getting item information...")
        items = self.data_processor.get_items_by_numbers(numbers)
        logger.info(f"Retrieved {len(items)} items")

        # Step 3: 必殺技判定
        logger.info("Step 3: Detecting hissatsuwaza...")
        hissatsus = self.data_processor.detect_hissatsuwaza(numbers)
        logger.info(f"Detected {len(hissatsus)} hissatsuwaza")

        # Step 4: 画像生成
        logger.info("Step 4: Generating result image...")
        image_path = self.image_processor.create_result_image(
            items,
            hissatsus,
            birthdate,
            birthtime,
            name
        )
        logger.info(f"Generated image: {image_path}")

        return image_path, numbers, items, hissatsus

    async def get_result_summary(
        self,
        birthdate: str,
        birthtime: str,
        name: str = None
    ) -> dict:
        """
        結果のサマリー情報を取得（フロントエンド表示用の完全な情報）

        Args:
            birthdate: 生年月日 (YYYY-MM-DD形式)
            birthtime: 時刻 (HH:MM形式)
            name: 名前（オプション）

        Returns:
            結果サマリーの辞書
        """
        image_path, numbers, items, hissatsus = await self.generate_dungeon_result(
            birthdate, birthtime, name
        )

        # 必殺技成立数字のペアを取得
        hissatsu_pairs = self.data_processor.get_hissatsu_pair_numbers(numbers)

        # 必殺技成立数字を抽出（赤字表示用）
        hissatsu_numbers = set()
        for pair in hissatsu_pairs.values():
            hissatsu_numbers.update(pair)

        # 色ごとの枚数情報を取得
        color_counts = self.data_processor.get_color_counts(items)

        # 動き方の説明を取得
        actions = self.data_processor.get_all_actions()

        # 画像パスをWeb URLに変換するヘルパー関数
        def convert_image_path_to_url(image_path: str) -> str:
            if not image_path:
                return ""
            # 絶対パスからファイル名を抽出し、/images/配下のパスに変換
            import os
            # database/images/item/1.jpg -> /images/item/1.jpg
            # database/images/Hissatsuwaza/1_h.jpg -> /images/Hissatsuwaza/1_h.jpg
            parts = image_path.split(os.sep)
            if 'images' in parts:
                idx = parts.index('images')
                relative_path = '/'.join(parts[idx:])
                return f'/{relative_path}'
            return ""

        return {
            'image_path': image_path,
            'name': name,
            'birthdate': birthdate,
            'birthtime': birthtime,
            'numbers': numbers,
            'hissatsu_numbers': list(hissatsu_numbers),  # 必殺技成立数字（赤字表示用）
            'hissatsu_pairs': hissatsu_pairs,  # {必殺技No: [数字1, 数字2]}
            'item_count': len(items),
            'hissatsu_count': len(hissatsus),
            'color_counts': color_counts,  # 色ごとの枚数情報
            'actions': actions,  # 動き方の説明
            'items': [
                {
                    'no': item.no,
                    'name': item.name,
                    'pair_no': item.pair_no,
                    'pair_name': item.pair_name,
                    'hissatsu_no': item.hissatsu_no,
                    'hissatsu_name': item.hissatsu_name,
                    'color': item.color,
                    'movement': item.movement,
                    'description': item.description,
                    'on_state': item.on_state,
                    'off_state': item.off_state,
                    'image_url': convert_image_path_to_url(item.image_path),
                }
                for item in items
            ],
            'hissatsus': [
                {
                    'hissatsu_no': h.hissatsu_no,
                    'name': h.name,
                    'color': h.color,
                    'meaning': h.meaning,
                    'movement': h.movement,
                    'basic_posture': h.basic_posture,
                    'talent': h.talent,
                    'characteristics': h.characteristics,
                    'advice': h.advice,
                    'on_state': h.on_state,
                    'off_state': h.off_state,
                    'image_url': convert_image_path_to_url(h.image_path),
                }
                for h in hissatsus
            ]
        }
