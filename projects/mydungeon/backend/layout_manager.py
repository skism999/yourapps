"""
画像レイアウト管理モジュール
アイテムと必殺技の配置順序を決定する
"""
from typing import List, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import ItemInfo, HissatsuInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayoutManager:
    """画像配置を管理するクラス"""

    # 色の系統定義
    COLOR_GROUPS = {
        '赤系': ['赤', '桃'],
        '緑系': ['緑', '黄緑'],
        '青系': ['青', '水'],
        '黄系': ['黄']
    }

    # 系統の優先順位（上から配置する順）
    GROUP_PRIORITY = ['赤系', '緑系', '青系', '黄系']

    # 各色の優先順位（系統内での左から右への順序）
    COLOR_PRIORITY = {
        '赤系': ['赤', '桃'],
        '緑系': ['緑', '黄緑'],
        '青系': ['青', '水'],
        '黄系': ['黄']
    }

    @classmethod
    def get_color_group(cls, color: str) -> str:
        """
        色から系統を取得

        Args:
            color: 色名（例: '赤', '青', '黄緑'）

        Returns:
            系統名（例: '赤系', '青系'）
        """
        for group, colors in cls.COLOR_GROUPS.items():
            if color in colors:
                return group

        logger.warning(f"Unknown color: {color}, defaulting to '赤系'")
        return '赤系'  # デフォルト

    @classmethod
    def sort_items(
        cls,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo]
    ) -> Tuple[List[HissatsuInfo], List[ItemInfo]]:
        """
        アイテムと必殺技を配置ルールに基づいてソート

        配置ルール:
        1. 色の優先度（上から）: 赤系 → 緑系 → 青系 → 黄系
        2. 各系統内で:
           - 必殺技があれば一番左（番号の若い順）
           - 必殺技がなければ番号の若い順

        Args:
            items: アイテム情報のリスト
            hissatsus: 必殺技情報のリスト

        Returns:
            (ソートされた必殺技リスト, ソートされたアイテムリスト)
        """
        # 必殺技をソート（番号の若い順）
        sorted_hissatsus = sorted(hissatsus, key=lambda h: h.hissatsu_no)

        # アイテムを色系統でグループ化
        grouped_items = {group: [] for group in cls.GROUP_PRIORITY}

        for item in items:
            color_group = cls.get_color_group(item.color)
            grouped_items[color_group].append(item)

        # 各グループ内でソート（色ごとに分けてから、必殺技優先、番号順）
        for group in cls.GROUP_PRIORITY:
            color_order = cls.COLOR_PRIORITY[group]

            # 色の順序を数値化（赤→桃、青→水など）
            def get_color_priority(item):
                try:
                    return color_order.index(item.color)
                except ValueError:
                    return 999  # 未知の色は最後

            grouped_items[group].sort(
                key=lambda item: (
                    get_color_priority(item),  # 色の優先順位
                    0 if item.hissatsu_no is not None else 1,  # 必殺技あり優先
                    item.no  # 番号の若い順
                )
            )

        # 優先順位に従って結合
        sorted_items = []
        for group in cls.GROUP_PRIORITY:
            sorted_items.extend(grouped_items[group])

        logger.info(f"Sorted {len(sorted_items)} items into layout order")
        logger.debug(f"Layout order: {[item.no for item in sorted_items]}")

        return sorted_hissatsus, sorted_items

    @classmethod
    def get_layout_info(
        cls,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo]
    ) -> dict:
        """
        レイアウト情報を取得（デバッグ用）

        Returns:
            レイアウト情報の辞書
        """
        sorted_hissatsus, sorted_items = cls.sort_items(items, hissatsus)

        layout_info = {
            'hissatsus': [
                {
                    'no': h.hissatsu_no,
                    'name': h.name,
                    'color': h.color
                }
                for h in sorted_hissatsus
            ],
            'items_by_group': {}
        }

        # 色系統ごとにアイテムを分類
        for group in cls.GROUP_PRIORITY:
            group_items = [
                item for item in sorted_items
                if cls.get_color_group(item.color) == group
            ]
            layout_info['items_by_group'][group] = [
                {
                    'no': item.no,
                    'name': item.name,
                    'color': item.color,
                    'has_hissatsu': item.hissatsu_no is not None,
                    'hissatsu_no': item.hissatsu_no
                }
                for item in group_items
            ]

        return layout_info


# テスト用
if __name__ == "__main__":
    from backend.data_processor import DataProcessor

    # 1991年9月16日13時50分のテストデータ
    test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]

    processor = DataProcessor()
    items = processor.get_items_by_numbers(test_numbers)
    hissatsus = processor.detect_hissatsuwaza(test_numbers)

    print("=" * 70)
    print("レイアウトマネージャーテスト")
    print("=" * 70)

    # レイアウト情報を取得
    layout_info = LayoutManager.get_layout_info(items, hissatsus)

    # 必殺技
    print("\n【必殺技】")
    if layout_info['hissatsus']:
        for h in layout_info['hissatsus']:
            print(f"  必殺No.{h['no']:2d}: {h['name']:15s} ({h['color']})")
    else:
        print("  (なし)")

    # 色系統ごとにアイテムを表示
    print("\n【アイテム】")
    for group in LayoutManager.GROUP_PRIORITY:
        group_items = layout_info['items_by_group'][group]
        if group_items:
            print(f"\n{group}:")
            for item in group_items:
                hissatsu_mark = "★" if item['has_hissatsu'] else " "
                hissatsu_info = f"(必殺No.{item['hissatsu_no']})" if item['has_hissatsu'] else ""
                print(f"  {hissatsu_mark} No.{item['no']:2d}: {item['name']:15s} ({item['color']}) {hissatsu_info}")

    # ソート後の順序を表示
    sorted_hissatsus, sorted_items = LayoutManager.sort_items(items, hissatsus)

    print("\n【配置順序】")
    position = 1

    # 必殺技
    if sorted_hissatsus:
        print("\n必殺技セクション:")
        for h in sorted_hissatsus:
            print(f"  {position}. 必殺No.{h.hissatsu_no}: {h.name} ({h.color})")
            position += 1

    # アイテム
    print("\nアイテムセクション:")
    current_group = None
    for item in sorted_items:
        group = LayoutManager.get_color_group(item.color)
        if group != current_group:
            print(f"\n  [{group}]")
            current_group = group

        hissatsu_mark = "★" if item.hissatsu_no else " "
        print(f"  {position}. {hissatsu_mark} No.{item.no}: {item.name} ({item.color})")
        position += 1

    print("\n" + "=" * 70)
    print(f"合計: 必殺技 {len(sorted_hissatsus)}個 + アイテム {len(sorted_items)}個 = {len(sorted_hissatsus) + len(sorted_items)}個")
    print("=" * 70)
