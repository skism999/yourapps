"""
相性診断プロセッサー
2人の数字から相性必殺技を3つのカテゴリに分類
"""
import pandas as pd
from typing import List, Dict, Set, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import HissatsuInfo
from backend.data_processor import DataProcessor
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompatibilityProcessor:
    """相性診断の必殺技カテゴリ分類を行うクラス"""

    def __init__(self, data_processor: DataProcessor):
        """
        Args:
            data_processor: DataProcessorインスタンス
        """
        self.data_processor = data_processor

    def categorize_special_moves(
        self,
        person1_numbers: List[int],
        person2_numbers: List[int]
    ) -> Dict[str, List[HissatsuInfo]]:
        """
        相性必殺技を3つのカテゴリに分類

        カテゴリ:
        1. joint: 二人で発動する必殺技（person1がAのみ、person2がBのみ）
        2. person1_synergy: person1だけで発動するが相手がいて相乗効果がある（person1がA+B、person2がAまたはB）
        3. person2_synergy: person2だけで発動するがあなたがいて相乗効果がある（person2がA+B、person1がAまたはB）

        Args:
            person1_numbers: person1の数字リスト
            person2_numbers: person2の数字リスト

        Returns:
            {
                'joint': [HissatsuInfo, ...],
                'person1_synergy': [HissatsuInfo, ...],
                'person2_synergy': [HissatsuInfo, ...]
            }
        """
        person1_set = set(person1_numbers)
        person2_set = set(person2_numbers)

        joint_hissatsus = []
        both_have_hissatsus = []
        person1_synergy_hissatsus = []
        person2_synergy_hissatsus = []

        # 処理済みペアを記録（重複防止）
        processed_pairs: Set[Tuple[int, int, int]] = set()

        # item_dfの全行をループ
        for _, item_row in self.data_processor.item_df.iterrows():
            if pd.notna(item_row['対No']) and pd.notna(item_row['必殺No']):
                num_a = int(item_row['No'])
                num_b = int(item_row['対No'])
                hissatsu_no = int(item_row['必殺No'])

                # 重複チェック（小さい番号を先にして正規化）
                pair_key = tuple(sorted([num_a, num_b]) + [hissatsu_no])
                if pair_key in processed_pairs:
                    continue

                # person1とperson2が各数字を持っているかチェック
                person1_has_a = num_a in person1_set
                person1_has_b = num_b in person1_set
                person2_has_a = num_a in person2_set
                person2_has_b = num_b in person2_set

                # カテゴリ1: 二人で発動する必殺技
                # person1がAのみ、person2がBのみ（または逆）
                if ((person1_has_a and not person1_has_b and person2_has_b and not person2_has_a) or
                    (person1_has_b and not person1_has_a and person2_has_a and not person2_has_b)):

                    hissatsu_info = self._get_hissatsu_info(hissatsu_no)
                    if hissatsu_info and hissatsu_info not in joint_hissatsus:
                        joint_hissatsus.append(hissatsu_info)
                        processed_pairs.add(pair_key)
                        logger.info(f"Joint hissatsu detected: {hissatsu_info.name} (No.{num_a}, No.{num_b})")

                # カテゴリ2: お互いが持っている必殺技（相乗効果×2）
                # person1もperson2もA+B（両方）を持っている
                elif person1_has_a and person1_has_b and person2_has_a and person2_has_b:
                    hissatsu_info = self._get_hissatsu_info(hissatsu_no)
                    if hissatsu_info and hissatsu_info not in both_have_hissatsus:
                        both_have_hissatsus.append(hissatsu_info)
                        processed_pairs.add(pair_key)
                        logger.info(f"Both have hissatsu detected: {hissatsu_info.name} (No.{num_a}, No.{num_b})")

                # カテゴリ3: person1の相乗効果
                # person1がA+B、person2がAまたはB（ただしperson2がA+Bではない）
                elif person1_has_a and person1_has_b and (person2_has_a or person2_has_b) and not (person2_has_a and person2_has_b):
                    hissatsu_info = self._get_hissatsu_info(hissatsu_no)
                    if hissatsu_info and hissatsu_info not in person1_synergy_hissatsus:
                        person1_synergy_hissatsus.append(hissatsu_info)
                        processed_pairs.add(pair_key)
                        logger.info(f"Person1 synergy hissatsu detected: {hissatsu_info.name} (No.{num_a}, No.{num_b})")

                # カテゴリ4: person2の相乗効果
                # person2がA+B、person1がAまたはB（ただしperson1がA+Bではない）
                elif person2_has_a and person2_has_b and (person1_has_a or person1_has_b) and not (person1_has_a and person1_has_b):
                    hissatsu_info = self._get_hissatsu_info(hissatsu_no)
                    if hissatsu_info and hissatsu_info not in person2_synergy_hissatsus:
                        person2_synergy_hissatsus.append(hissatsu_info)
                        processed_pairs.add(pair_key)
                        logger.info(f"Person2 synergy hissatsu detected: {hissatsu_info.name} (No.{num_a}, No.{num_b})")

        logger.info(f"Categorized hissatsus: joint={len(joint_hissatsus)}, "
                   f"both_have={len(both_have_hissatsus)}, "
                   f"person1_synergy={len(person1_synergy_hissatsus)}, "
                   f"person2_synergy={len(person2_synergy_hissatsus)}")

        return {
            'joint': joint_hissatsus,
            'both_have': both_have_hissatsus,
            'person1_synergy': person1_synergy_hissatsus,
            'person2_synergy': person2_synergy_hissatsus
        }

    def get_colored_numbers(
        self,
        person1_numbers: List[int],
        person2_numbers: List[int],
        categorized_hissatsus: Dict[str, List[HissatsuInfo]]
    ) -> Tuple[Dict[str, Set[int]], Dict[str, Set[int]]]:
        """
        数字を色分けする（紫=joint, 赤=both_have, 青=person1_synergy, 緑=person2_synergy, グレー=solo）

        優先順位:
        1. 紫（最優先）: joint_numbers
        2. 赤: both_have_numbers
        3. 青: person1_synergy_numbers
        4. 緑: person2_synergy_numbers
        5. グレー: solo_hissatsu_numbers

        Args:
            person1_numbers: person1の数字リスト
            person2_numbers: person2の数字リスト
            categorized_hissatsus: categorize_special_moves()の結果

        Returns:
            (person1_colored, person2_colored)
            各辞書は {'joint': {1,2,3}, 'both_have': {4,5}, 'person1_synergy': {6,7}, 'person2_synergy': {8,9}, 'solo': {10,11}}
        """
        # 各カテゴリに含まれる数字を抽出
        joint_numbers = self._extract_numbers_from_hissatsus(categorized_hissatsus['joint'])
        both_have_numbers = self._extract_numbers_from_hissatsus(categorized_hissatsus['both_have'])
        person1_synergy_numbers = self._extract_numbers_from_hissatsus(categorized_hissatsus['person1_synergy'])
        person2_synergy_numbers = self._extract_numbers_from_hissatsus(categorized_hissatsus['person2_synergy'])

        # person1の単独必殺技の数字を取得
        person1_solo_hissatsus = self.data_processor.detect_hissatsuwaza(person1_numbers)
        person1_solo_numbers = self._extract_numbers_from_hissatsus(person1_solo_hissatsus)

        # person2の単独必殺技の数字を取得
        person2_solo_hissatsus = self.data_processor.detect_hissatsuwaza(person2_numbers)
        person2_solo_numbers = self._extract_numbers_from_hissatsus(person2_solo_hissatsus)

        # person1の色分け（person1_synergyとperson2_synergyを分けて指定）
        person1_colored = self._classify_numbers_by_priority(
            set(person1_numbers),
            joint_numbers,
            both_have_numbers,
            person1_synergy_numbers,
            person2_synergy_numbers,
            person1_solo_numbers
        )

        # person2の色分け（person1_synergyとperson2_synergyを分けて指定）
        person2_colored = self._classify_numbers_by_priority(
            set(person2_numbers),
            joint_numbers,
            both_have_numbers,
            person1_synergy_numbers,
            person2_synergy_numbers,
            person2_solo_numbers
        )

        return person1_colored, person2_colored

    def _get_hissatsu_info(self, hissatsu_no: int) -> HissatsuInfo:
        """必殺技番号からHissatsuInfoを取得"""
        hissatsu_row = self.data_processor.hissatsu_df[
            self.data_processor.hissatsu_df['必殺No'] == hissatsu_no
        ]

        if len(hissatsu_row) == 0:
            logger.warning(f"Hissatsu not found: {hissatsu_no}")
            return None

        row = hissatsu_row.iloc[0]

        # 画像パスを取得
        image_path = self.data_processor._find_image_path(
            hissatsu_no,
            settings.HISSATSU_IMAGES_DIR,
            suffix='_h'
        )

        return HissatsuInfo(
            hissatsu_no=int(row['必殺No']),
            name=row['必殺技名'],
            color=row['色'],
            meaning=row['意味'],
            movement=row['動き方'],
            basic_posture=row['基本姿勢'],
            talent=row['才能'],
            characteristics=row['特性'],
            advice=row['アドバイス'],
            on_state=row['ON'],
            off_state=row['OFF'],
            image_path=image_path
        )

    def _extract_numbers_from_hissatsus(self, hissatsus: List[HissatsuInfo]) -> Set[int]:
        """必殺技リストから関連する数字を抽出"""
        numbers = set()

        for hissatsu in hissatsus:
            # item_dfから必殺技に関連する数字を取得
            related_items = self.data_processor.item_df[
                self.data_processor.item_df['必殺No'] == hissatsu.hissatsu_no
            ]

            for _, item_row in related_items.iterrows():
                numbers.add(int(item_row['No']))
                if pd.notna(item_row['対No']):
                    numbers.add(int(item_row['対No']))

        return numbers

    def _classify_numbers_by_priority(
        self,
        all_numbers: Set[int],
        joint_numbers: Set[int],
        both_have_numbers: Set[int],
        person1_synergy_numbers: Set[int],
        person2_synergy_numbers: Set[int],
        solo_numbers: Set[int]
    ) -> Dict[str, Set[int]]:
        """
        数字を優先順位に従って分類

        優先順位: joint > person1_synergy > person2_synergy > both_have > solo > その他
        """
        classified = {
            'joint': set(),
            'both_have': set(),
            'person1_synergy': set(),
            'person2_synergy': set(),
            'solo': set()
        }

        for num in all_numbers:
            if num in joint_numbers:
                classified['joint'].add(num)
            elif num in person1_synergy_numbers:
                classified['person1_synergy'].add(num)
            elif num in person2_synergy_numbers:
                classified['person2_synergy'].add(num)
            elif num in both_have_numbers:
                classified['both_have'].add(num)
            elif num in solo_numbers:
                classified['solo'].add(num)

        return classified
