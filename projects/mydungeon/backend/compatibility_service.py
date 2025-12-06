"""
相性診断サービス
2人分のスクレイピングから画像生成までの完全なフローを提供
"""
import logging
import asyncio
from typing import Dict, List
from backend.scraper import DungeonScraper
from backend.data_processor import DataProcessor
from backend.compatibility_processor import CompatibilityProcessor
from backend.compatibility_image_processor import CompatibilityImageProcessor
from backend.models import ItemInfo, HissatsuInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompatibilityService:
    """相性診断の完全なサービス"""

    def __init__(self):
        self.scraper = DungeonScraper()
        self.data_processor = DataProcessor()
        self.compatibility_processor = CompatibilityProcessor(self.data_processor)
        self.compatibility_image_processor = CompatibilityImageProcessor()

    async def generate_compatibility_result(
        self,
        person1_birthdate: str,
        person1_birthtime: str,
        person2_birthdate: str,
        person2_birthtime: str,
        person1_name: str = None,
        person2_name: str = None
    ) -> dict:
        """
        2人の生年月日時刻から相性診断結果を生成

        Args:
            person1_birthdate: person1の生年月日 (YYYY-MM-DD形式)
            person1_birthtime: person1の時刻 (HH:MM形式)
            person2_birthdate: person2の生年月日 (YYYY-MM-DD形式)
            person2_birthtime: person2の時刻 (HH:MM形式)
            person1_name: person1の名前（オプション）
            person2_name: person2の名前（オプション）

        Returns:
            相性診断結果の辞書
        """
        logger.info(f"Starting compatibility result generation")
        logger.info(f"Person1: {person1_birthdate} {person1_birthtime}")
        logger.info(f"Person2: {person2_birthdate} {person2_birthtime}")

        # Step 1: 並列スクレイピング
        logger.info("Step 1: Parallel scraping for both people...")
        person1_numbers, person2_numbers = await asyncio.gather(
            self.scraper.scrape_numbers(person1_birthdate, person1_birthtime),
            self.scraper.scrape_numbers(person2_birthdate, person2_birthtime)
        )
        logger.info(f"Person1 numbers ({len(person1_numbers)}): {person1_numbers}")
        logger.info(f"Person2 numbers ({len(person2_numbers)}): {person2_numbers}")

        # Step 2: アイテム情報取得
        logger.info("Step 2: Getting item information for both people...")
        person1_items = self.data_processor.get_items_by_numbers(person1_numbers)
        person2_items = self.data_processor.get_items_by_numbers(person2_numbers)
        logger.info(f"Person1 items: {len(person1_items)}, Person2 items: {len(person2_items)}")

        # Step 3: 単独必殺技検出
        logger.info("Step 3: Detecting solo hissatsuwaza for both people...")
        person1_solo_hissatsus = self.data_processor.detect_hissatsuwaza(person1_numbers)
        person2_solo_hissatsus = self.data_processor.detect_hissatsuwaza(person2_numbers)
        logger.info(f"Person1 solo hissatsus: {len(person1_solo_hissatsus)}, "
                   f"Person2 solo hissatsus: {len(person2_solo_hissatsus)}")

        # Step 4: 相性必殺技カテゴリ分類
        logger.info("Step 4: Categorizing compatibility hissatsuwaza...")
        categorized = self.compatibility_processor.categorize_special_moves(
            person1_numbers, person2_numbers
        )

        # Step 5: 数字の色分け
        logger.info("Step 5: Coloring numbers...")
        person1_colored, person2_colored = self.compatibility_processor.get_colored_numbers(
            person1_numbers, person2_numbers, categorized
        )

        # Step 6: 画像生成
        logger.info("Step 6: Generating compatibility image...")
        image_path = self.compatibility_image_processor.create_compatibility_image(
            categorized['joint'],
            categorized['both_have'],
            categorized['person1_synergy'],
            categorized['person2_synergy'],
            person1_name, person1_birthdate, person1_birthtime,
            person2_name, person2_birthdate, person2_birthtime
        )
        logger.info(f"Generated compatibility image: {image_path}")

        # Step 7: 色ごとの枚数を計算（2人分を合計）
        combined_numbers = list(set(person1_numbers + person2_numbers))
        combined_items = self.data_processor.get_items_by_numbers(combined_numbers)
        color_counts = self.data_processor.get_color_counts(combined_items)

        # Step 8: 動き方の説明を取得
        actions = self.data_processor.get_all_actions()

        # Step 9: レスポンス構築
        logger.info("Step 9: Building response...")

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

        result = {
            'image_path': image_path,
            'person1': {
                'name': person1_name,
                'birthdate': person1_birthdate,
                'birthtime': person1_birthtime,
                'numbers': person1_numbers,
                'joint_numbers': list(person1_colored.get('joint', set())),
                'both_have_numbers': list(person1_colored.get('both_have', set())),
                'person1_synergy_numbers': list(person1_colored.get('person1_synergy', set())),
                'person2_synergy_numbers': list(person1_colored.get('person2_synergy', set())),
                'solo_hissatsu_numbers': list(person1_colored.get('solo', set())),
                'items': [{**item.dict(), 'image_url': convert_image_path_to_url(item.image_path)} for item in person1_items],
                'solo_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in person1_solo_hissatsus]
            },
            'person2': {
                'name': person2_name,
                'birthdate': person2_birthdate,
                'birthtime': person2_birthtime,
                'numbers': person2_numbers,
                'joint_numbers': list(person2_colored.get('joint', set())),
                'both_have_numbers': list(person2_colored.get('both_have', set())),
                'person1_synergy_numbers': list(person2_colored.get('person1_synergy', set())),
                'person2_synergy_numbers': list(person2_colored.get('person2_synergy', set())),
                'solo_hissatsu_numbers': list(person2_colored.get('solo', set())),
                'items': [{**item.dict(), 'image_url': convert_image_path_to_url(item.image_path)} for item in person2_items],
                'solo_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in person2_solo_hissatsus]
            },
            'joint_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in categorized['joint']],
            'both_have_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in categorized['both_have']],
            'person1_synergy_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in categorized['person1_synergy']],
            'person2_synergy_hissatsus': [{**h.dict(), 'image_url': convert_image_path_to_url(h.image_path)} for h in categorized['person2_synergy']],
            'color_counts': color_counts,
            'actions': actions
        }

        logger.info("Compatibility result generation completed!")
        return result
