"""
画像処理モジュール
アイテムと必殺技の画像を結合して1枚の画像を生成
"""
from PIL import Image, ImageDraw, ImageFont
from typing import List
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings
from backend.models import ItemInfo, HissatsuInfo
from backend.layout_manager import LayoutManager
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """画像の結合処理"""

    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # 画像設定
        self.item_width = 188  # アイテム画像の横幅（元の250の75%）
        self.hissatsu_width = 376  # 必殺技画像の横幅（アイテムの2倍）
        self.image_height = 250  # 画像の高さ
        self.color_gap = 30  # 色が変わる時の隙間
        self.row_gap = 40  # 行間の隙間（色系統ごと）
        self.info_height = 0  # 情報表示エリアの高さ（テキストなし）
        self.header_height = 100  # ヘッダーの高さ（拡大）
        self.side_padding = 20  # 左右の余白

        # 色設定
        self.bg_color = (245, 245, 250)  # 背景色（薄い青グレー）
        self.text_color = (40, 40, 40)  # テキスト色
        self.header_color = (100, 100, 200)  # ヘッダーテキスト色

        # フォント設定
        self.font_path = None  # システムフォントを使用
        try:
            # 日本語フォントの候補を試す
            font_candidates = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            ]
            for font_path in font_candidates:
                if os.path.exists(font_path):
                    self.font_path = font_path
                    break

            if self.font_path:
                self.font_small = ImageFont.truetype(self.font_path, 12)
                self.font_medium = ImageFont.truetype(self.font_path, 14)
                self.font_large = ImageFont.truetype(self.font_path, 20)
                self.font_title = ImageFont.truetype(self.font_path, 28)
            else:
                logger.warning("TrueType font not found, using default font")
                self.font_small = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_large = ImageFont.load_default()
                self.font_title = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Font loading error: {e}, using default font")
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_title = ImageFont.load_default()

    def create_result_image(
        self,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo],
        birthdate: str = None,
        birthtime: str = None,
        name: str = None
    ) -> str:
        """
        アイテムと必殺技の画像を1枚に結合

        Args:
            items: アイテム情報のリスト
            hissatsus: 必殺技情報のリスト
            birthdate: 生年月日（オプション）
            birthtime: 時刻（オプション）
            name: 名前（オプション）

        Returns:
            生成された画像のファイルパス
        """
        # レイアウトマネージャーでソート
        sorted_hissatsus, sorted_items = LayoutManager.sort_items(items, hissatsus)

        # 色系統と色ごとにグループ化
        color_groups = self._group_by_color_system(sorted_items, sorted_hissatsus)

        # 各行の幅を計算して最大幅を求める
        max_width = 0
        row_count = 0

        for group_name in LayoutManager.GROUP_PRIORITY:
            group_data = color_groups[group_name]

            # この系統に何かアイテムがあるか確認
            has_items = False
            for color in LayoutManager.COLOR_PRIORITY[group_name]:
                if group_data[color]['items'] or group_data[color]['hissatsus']:
                    has_items = True
                    break

            if not has_items:
                continue

            # この系統の行の幅を計算
            row_width = self.side_padding
            prev_color = None

            for color in LayoutManager.COLOR_PRIORITY[group_name]:
                color_data = group_data[color]
                if not color_data['items'] and not color_data['hissatsus']:
                    continue

                # 色が変わる時は隙間を追加
                if prev_color is not None:
                    row_width += self.color_gap

                # 必殺技の幅を追加
                for _ in color_data['hissatsus']:
                    row_width += self.hissatsu_width

                # アイテムの幅を追加
                for _ in color_data['items']:
                    row_width += self.item_width

                prev_color = color

            row_width += self.side_padding
            max_width = max(max_width, row_width)
            row_count += 1

        # キャンバスサイズ
        canvas_width = max_width
        canvas_height = (
            self.header_height +
            row_count * (self.image_height + self.info_height + self.row_gap) +
            self.row_gap
        )

        # 新しい画像を作成
        result_image = Image.new('RGB', (canvas_width, canvas_height), self.bg_color)
        draw = ImageDraw.Draw(result_image)

        # ヘッダーを描画
        self._draw_header(draw, canvas_width, birthdate, birthtime, name)

        # 色系統ごとに配置
        current_y = self.header_height + self.row_gap

        for group_name in LayoutManager.GROUP_PRIORITY:
            group_data = color_groups[group_name]

            # この系統に何かアイテムがあるか確認
            has_items = False
            for color in LayoutManager.COLOR_PRIORITY[group_name]:
                if group_data[color]['items'] or group_data[color]['hissatsus']:
                    has_items = True
                    break

            if not has_items:
                continue

            # この行の配置開始
            current_x = self.side_padding
            prev_color = None

            for color in LayoutManager.COLOR_PRIORITY[group_name]:
                color_data = group_data[color]
                if not color_data['items'] and not color_data['hissatsus']:
                    continue

                # 色が変わる時は隙間を追加
                if prev_color is not None:
                    current_x += self.color_gap

                # 必殺技を配置
                for hissatsu in color_data['hissatsus']:
                    self._draw_item_at_xy(
                        result_image,
                        draw,
                        current_x,
                        current_y,
                        self.hissatsu_width,
                        hissatsu.image_path,
                        f"Hissatsu No.{hissatsu.hissatsu_no}: {hissatsu.name}",
                        hissatsu.color,
                        hissatsu.meaning,
                        is_hissatsu=True
                    )
                    current_x += self.hissatsu_width

                # アイテムを配置
                for item in color_data['items']:
                    hissatsu_info = f"(Hissatsu No.{item.hissatsu_no})" if item.hissatsu_no else ""
                    self._draw_item_at_xy(
                        result_image,
                        draw,
                        current_x,
                        current_y,
                        self.item_width,
                        item.image_path,
                        f"No.{item.no}: {item.name}",
                        item.color,
                        item.movement + " " + hissatsu_info,
                        is_hissatsu=False
                    )
                    current_x += self.item_width

                prev_color = color

            # 次の行へ
            current_y += self.image_height + self.info_height + self.row_gap

        # ファイル名生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"result_{timestamp}.png")
        result_image.save(output_path, quality=95)

        logger.info(f"Result image saved: {output_path}")
        return output_path

    def _group_by_color_system(
        self,
        items: List[ItemInfo],
        hissatsus: List[HissatsuInfo]
    ) -> dict:
        """
        アイテムと必殺技を色系統と色でグループ化

        Returns:
            色系統ごと、さらに色ごとのアイテムと必殺技の辞書
        """
        groups = {}
        for group_name in LayoutManager.GROUP_PRIORITY:
            groups[group_name] = {}
            # 各色系統内の色でさらに分ける
            for color in LayoutManager.COLOR_PRIORITY[group_name]:
                groups[group_name][color] = {
                    'hissatsus': [],
                    'items': []
                }

        # 必殺技を色系統と色でグループ化
        for hissatsu in hissatsus:
            group = LayoutManager.get_color_group(hissatsu.color)
            if hissatsu.color in groups[group]:
                groups[group][hissatsu.color]['hissatsus'].append(hissatsu)

        # アイテムを色系統と色でグループ化
        for item in items:
            group = LayoutManager.get_color_group(item.color)
            if item.color in groups[group]:
                groups[group][item.color]['items'].append(item)

        return groups

    def _draw_header(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        birthdate: str = None,
        birthtime: str = None,
        name: str = None
    ):
        """ヘッダーを描画"""
        # タイトル
        title = "My Dungeon Result"
        draw.text(
            (width // 2, 25),
            title,
            fill=self.header_color,
            font=self.font_title,
            anchor="mm"
        )

        # 名前
        if name:
            draw.text(
                (width // 2, 60),
                name,
                fill=self.text_color,
                font=self.font_large,
                anchor="mm"
            )

        # 日時情報
        if birthdate and birthtime:
            # 名前がある場合は位置を下げる
            y_position = 85 if name else 55
            date_text = f"Birthdate: {birthdate} {birthtime}"
            draw.text(
                (width // 2, y_position),
                date_text,
                fill=self.text_color,
                font=self.font_medium,
                anchor="mm"
            )

    def _draw_item_at_xy(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        image_path: str,
        title: str,
        color: str,
        description: str,
        is_hissatsu: bool = False
    ):
        """指定されたx, y座標にアイテムまたは必殺技を描画"""
        # 画像を読み込んで配置
        if image_path and os.path.exists(image_path):
            try:
                item_img = Image.open(image_path)
                item_img = item_img.resize((width, self.image_height), Image.Resampling.LANCZOS)
                image.paste(item_img, (x, y))
            except Exception as e:
                logger.error(f"Error loading image {image_path}: {e}")
                # エラー時はグレーボックス
                draw.rectangle(
                    [x, y, x + width, y + self.image_height],
                    fill='gray'
                )
        else:
            # 画像がない場合はグレーボックス
            draw.rectangle(
                [x, y, x + width, y + self.image_height],
                fill='lightgray'
            )
            # "No Image"テキスト
            draw.text(
                (x + width//2, y + self.image_height//2),
                "No Image",
                fill=self.text_color,
                font=self.font_medium,
                anchor="mm"
            )

    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """テキストを指定文字数で折り返し"""
        if len(text) <= max_length:
            return [text]

        lines = []
        current_line = ""

        for char in text:
            if len(current_line) + 1 <= max_length:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines


# テスト用
if __name__ == "__main__":
    from backend.data_processor import DataProcessor

    # 1991年9月16日13時50分のテストデータ
    test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]
    birthdate = "1991-09-16"
    birthtime = "13:50"

    processor = DataProcessor()
    items = processor.get_items_by_numbers(test_numbers)
    hissatsus = processor.detect_hissatsuwaza(test_numbers)

    print("=" * 70)
    print("画像プロセッサーテスト")
    print("=" * 70)
    print(f"\nアイテム数: {len(items)}")
    print(f"必殺技数: {len(hissatsus)}")

    img_processor = ImageProcessor()
    output_path = img_processor.create_result_image(items, hissatsus, birthdate, birthtime)

    print(f"\n生成された画像: {output_path}")
    print(f"ファイルサイズ: {os.path.getsize(output_path) / 1024:.1f} KB")

    if os.path.exists(output_path):
        print("\n✓ 画像生成成功")
    else:
        print("\n✗ 画像生成失敗")

    print("\n" + "=" * 70)
