import pandas as pd
from typing import List, Dict, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings
from backend.models import ItemInfo, HissatsuInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """CSVデータの読み込みとマッチング処理"""

    def __init__(self):
        self.item_df = None
        self.hissatsu_df = None
        self.color_meaning_df = None
        self.action_df = None
        self.load_csv_data()

    def load_csv_data(self):
        """CSVファイルを読み込む"""
        try:
            # item_list.csvの読み込み
            self.item_df = pd.read_csv(
                settings.ITEM_CSV,
                encoding='utf-8',
                header=0  # 1行目をヘッダーとして使用
            )

            # 最初の列名から行番号と矢印を除去（例: "1→No" → "No"）
            first_col = self.item_df.columns[0]
            if '→' in first_col:
                self.item_df.columns = [first_col.split('→')[1]] + list(self.item_df.columns[1:])

            # 列名のクリーニング（前後の空白を削除）
            self.item_df.columns = self.item_df.columns.str.strip()

            logger.info(f"Loaded {len(self.item_df)} items from CSV")
            logger.info(f"Columns: {self.item_df.columns.tolist()}")

            # hissatsuwaza_list.csvの読み込み
            self.hissatsu_df = pd.read_csv(
                settings.HISSATSU_CSV,
                encoding='utf-8',
                header=0
            )

            # 最初の列名から行番号と矢印を除去
            first_col = self.hissatsu_df.columns[0]
            if '→' in first_col:
                self.hissatsu_df.columns = [first_col.split('→')[1]] + list(self.hissatsu_df.columns[1:])

            # 列名のクリーニング
            self.hissatsu_df.columns = self.hissatsu_df.columns.str.strip()

            logger.info(f"Loaded {len(self.hissatsu_df)} hissatsuwaza from CSV")
            logger.info(f"Columns: {self.hissatsu_df.columns.tolist()}")

            # meaning_of_color.csvの読み込み
            self.color_meaning_df = pd.read_csv(
                settings.COLOR_MEANING_CSV,
                encoding='utf-8',
                header=0
            )
            self.color_meaning_df.columns = self.color_meaning_df.columns.str.strip()

            # 系統列の空欄を前の値で埋める（forward fill）
            self.color_meaning_df['系統'] = self.color_meaning_df['系統'].fillna(method='ffill')
            self.color_meaning_df['系統意味'] = self.color_meaning_df['系統意味'].fillna(method='ffill')

            logger.info(f"Loaded {len(self.color_meaning_df)} color meanings from CSV")

            # how_to_action.csvの読み込み
            self.action_df = pd.read_csv(
                settings.ACTION_CSV,
                encoding='utf-8',
                header=0
            )
            self.action_df.columns = self.action_df.columns.str.strip()
            logger.info(f"Loaded {len(self.action_df)} action descriptions from CSV")

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
                    name=str(item['アイテム名']),
                    pair_no=int(item['対No']) if pd.notna(item['対No']) else None,
                    pair_name=str(item['対アイテム名']) if pd.notna(item['対アイテム名']) else None,
                    hissatsu_no=int(item['必殺No']) if pd.notna(item['必殺No']) else None,
                    hissatsu_name=str(item['必殺技名']) if pd.notna(item['必殺技名']) else None,
                    color=str(item['色']),
                    movement=str(item['動き方']),
                    description=str(item['説明']),
                    on_state=str(item['ON']),
                    off_state=str(item['OFF']),
                    image_path=image_path
                ))
            else:
                logger.warning(f"Item No.{number} not found in CSV")

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
                                name=str(h['必殺技名']),
                                color=str(h['色']),
                                meaning=str(h['意味']),
                                movement=str(h['動き方']),
                                basic_posture=str(h['基本姿勢']),
                                talent=str(h['才能']),
                                characteristics=str(h['特性']),
                                advice=str(h['アドバイス']),
                                on_state=str(h['ON']),
                                off_state=str(h['OFF']),
                                image_path=image_path
                            ))
                        else:
                            logger.warning(f"Hissatsuwaza No.{hissatsu_no} not found in CSV")

        logger.info(f"Detected {len(hissatsus)} hissatsuwaza: {list(activated_hissatsu_nos)}")
        return hissatsus

    def get_hissatsu_pair_numbers(self, numbers: List[int]) -> Dict[int, List[int]]:
        """
        必殺技成立数字のペアを取得

        Args:
            numbers: スクレイピングで取得した数字のリスト

        Returns:
            {必殺技No: [数字1, 数字2]} の辞書
        """
        hissatsu_pairs = {}
        number_set = set(numbers)
        processed_pairs = set()

        for number in numbers:
            item_row = self.item_df[self.item_df['No'] == number]
            if not item_row.empty:
                item = item_row.iloc[0]
                pair_no = item['対No']
                hissatsu_no = item['必殺No']

                if (pd.notna(pair_no) and
                    int(pair_no) in number_set and
                    pd.notna(hissatsu_no)):

                    hissatsu_no = int(hissatsu_no)
                    pair_no = int(pair_no)

                    # ペアの順序を正規化（小さい方を先に）
                    pair_tuple = tuple(sorted([number, pair_no]))

                    if pair_tuple not in processed_pairs:
                        processed_pairs.add(pair_tuple)
                        hissatsu_pairs[hissatsu_no] = list(pair_tuple)

        return hissatsu_pairs

    def get_color_counts(self, items: List[ItemInfo]) -> Dict:
        """
        色ごとの枚数をカウント

        Args:
            items: アイテム情報のリスト

        Returns:
            色系統ごとの枚数情報
        """
        # 色ごとのカウント
        color_count = {}
        for item in items:
            color = item.color
            color_count[color] = color_count.get(color, 0) + 1

        # 色系統の情報を構築
        color_systems = []

        # 色系統の順序
        system_order = ['赤系', '緑系', '青系', '黄系']

        for system_name in system_order:
            # 該当する色系統の行を取得
            system_rows = self.color_meaning_df[
                self.color_meaning_df['系統'] == system_name
            ]

            if not system_rows.empty:
                # 系統の意味を取得（最初の行から）
                system_meaning = system_rows.iloc[0]['系統意味']

                colors_info = []
                total_count = 0

                # 各色の情報を取得
                for _, row in system_rows.iterrows():
                    color_name = row['色']
                    if pd.notna(color_name) and color_name:
                        color_meaning = row['色意味']
                        count = color_count.get(color_name, 0)

                        if count > 0:
                            colors_info.append({
                                'name': color_name,
                                'meaning': color_meaning,
                                'count': count
                            })
                            total_count += count

                if total_count > 0:
                    color_systems.append({
                        'name': system_name,
                        'meaning': system_meaning,
                        'total_count': total_count,
                        'colors': colors_info
                    })

        return {'color_systems': color_systems}

    def get_all_actions(self) -> List[Dict[str, str]]:
        """
        すべての動き方の説明を取得

        Returns:
            [{'action': '動き方', 'meaning': '意味'}, ...] のリスト
        """
        actions = []
        for _, row in self.action_df.iterrows():
            actions.append({
                'action': str(row['動き方']),
                'meaning': str(row['意味'])
            })
        return actions

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
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF']

        for ext in extensions:
            filename = f"{number}{suffix}{ext}"
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                logger.debug(f"Found image: {filepath}")
                return filepath

        # 見つからない場合は警告を出して空文字を返す
        logger.warning(f"Image not found: {number}{suffix} in {directory}")
        return ""


# テスト用
if __name__ == "__main__":
    processor = DataProcessor()

    # テスト: 1991年9月16日13時50分の結果
    test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]

    print("=" * 50)
    print("データ処理テスト")
    print("=" * 50)
    print(f"\n入力数字: {test_numbers}")
    print(f"数字の個数: {len(test_numbers)}")

    # アイテム情報を取得
    print("\n" + "=" * 50)
    print("アイテム情報")
    print("=" * 50)
    items = processor.get_items_by_numbers(test_numbers)
    print(f"\n取得したアイテム数: {len(items)}")
    for item in items:
        print(f"\nNo.{item.no}: {item.name}")
        print(f"  色: {item.color} | 動き方: {item.movement}")
        print(f"  対No: {item.pair_no} ({item.pair_name})")
        print(f"  必殺No: {item.hissatsu_no} ({item.hissatsu_name})")
        print(f"  画像: {os.path.basename(item.image_path) if item.image_path else 'なし'}")

    # 必殺技判定
    print("\n" + "=" * 50)
    print("必殺技判定")
    print("=" * 50)
    hissatsus = processor.detect_hissatsuwaza(test_numbers)
    print(f"\n発動した必殺技数: {len(hissatsus)}")
    for h in hissatsus:
        print(f"\n必殺No.{h.hissatsu_no}: {h.name}")
        print(f"  色: {h.color}")
        print(f"  意味: {h.meaning}")
        print(f"  画像: {os.path.basename(h.image_path) if h.image_path else 'なし'}")

    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)
