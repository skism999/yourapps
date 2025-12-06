"""
相性診断画像処理モジュール
2人の必殺技を4行レイアウトで表示
"""
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict
import os
import sys
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings
from backend.models import HissatsuInfo
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompatibilityImageProcessor:
    """相性診断画像の生成処理"""

    # 色の優先順位（左から右への配置順）
    COLOR_PRIORITY = ['赤', '桃', '緑', '黄緑', '青', '水', '黄']

    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # 画像設定
        self.hissatsu_width = 376  # 必殺技画像の横幅
        self.image_height = 250  # 画像の高さ
        self.max_per_line = 4  # 1行に最大4枚
        self.color_gap = 30  # 色が変わる時の隙間
        self.row_gap = 40  # 行間の隙間
        self.line_gap = 20  # 折り返し時の行間
        self.header_height = 150  # ヘッダーの高さ（2人用なので拡大）
        self.side_padding = 20  # 左右の余白
        self.label_height = 30  # 行ラベルの高さ

        # 色設定
        self.bg_color = (245, 245, 250)  # 背景色
        self.text_color = (40, 40, 40)  # テキスト色
        self.header_color = (100, 100, 200)  # ヘッダーテキスト色

        # フォント設定
        self.font_path = None
        try:
            font_candidates = [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            ]
            for font_path in font_candidates:
                if os.path.exists(font_path):
                    self.font_path = font_path
                    logger.info(f"Using font: {font_path}")
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

    def create_compatibility_image(
        self,
        joint_hissatsus: List[HissatsuInfo],
        both_have_hissatsus: List[HissatsuInfo],
        person1_synergy_hissatsus: List[HissatsuInfo],
        person2_synergy_hissatsus: List[HissatsuInfo],
        person1_name: str,
        person1_birthdate: str,
        person1_birthtime: str,
        person2_name: str,
        person2_birthdate: str,
        person2_birthtime: str
    ) -> str:
        """
        相性診断画像を生成

        Args:
            joint_hissatsus: 二人で発動する必殺技
            both_have_hissatsus: お互い持っている必殺技（相乗効果×2）
            person1_synergy_hissatsus: person1の相乗効果必殺技
            person2_synergy_hissatsus: person2の相乗効果必殺技
            person1_name: person1の名前
            person1_birthdate: person1の生年月日
            person1_birthtime: person1の時刻
            person2_name: person2の名前
            person2_birthdate: person2の生年月日
            person2_birthtime: person2の時刻

        Returns:
            生成された画像のファイルパス
        """
        logger.info("Creating compatibility image...")

        # 各行を色でグループ化
        row1_groups = self._group_by_color(joint_hissatsus)
        row2_groups = self._group_by_color(person1_synergy_hissatsus)
        row3_groups = self._group_by_color(person2_synergy_hissatsus)
        row4_groups = self._group_by_color(both_have_hissatsus)

        # 各行を折り返しレイアウトに変換
        row1_lines = self._layout_row_with_wrapping(row1_groups)
        row2_lines = self._layout_row_with_wrapping(row2_groups)
        row3_lines = self._layout_row_with_wrapping(row3_groups)
        row4_lines = self._layout_row_with_wrapping(row4_groups)

        # キャンバスサイズ計算
        max_width = self._calculate_max_width([row1_lines, row2_lines, row3_lines, row4_lines])
        total_height = self._calculate_total_height([row1_lines, row2_lines, row3_lines, row4_lines])

        # キャンバス作成
        canvas = Image.new('RGB', (max_width, total_height), self.bg_color)
        draw = ImageDraw.Draw(canvas)

        # ヘッダー描画
        current_y = self._draw_header(
            draw, max_width,
            person1_name, person1_birthdate, person1_birthtime,
            person2_name, person2_birthdate, person2_birthtime
        )

        # 行1: 二人で発動する必殺技
        current_y = self._draw_hissatsu_row(
            canvas, draw, row1_lines, current_y,
            "二人で発動する必殺技"
        )

        # 行2: person1の相乗効果
        person1_label = f"{person1_name or 'あなた'}だけで発動するが{person2_name or '相手'}がいて相乗効果がある必殺技"
        current_y = self._draw_hissatsu_row(
            canvas, draw, row2_lines, current_y,
            person1_label
        )

        # 行3: person2の相乗効果
        person2_label = f"{person2_name or '相手'}だけで発動するが{person1_name or 'あなた'}がいて相乗効果がある必殺技"
        current_y = self._draw_hissatsu_row(
            canvas, draw, row3_lines, current_y,
            person2_label
        )

        # 行4: お互い持っている必殺技（相乗効果×2）
        current_y = self._draw_hissatsu_row(
            canvas, draw, row4_lines, current_y,
            "お互い持っている必殺技（相乗効果×2）"
        )

        # 画像を保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(self.output_dir, f'compatibility_{timestamp}.png')
        canvas.save(output_path, 'PNG')
        logger.info(f"Compatibility image saved: {output_path}")

        return output_path

    def _group_by_color(self, hissatsus: List[HissatsuInfo]) -> Dict[str, List[HissatsuInfo]]:
        """必殺技を色でグループ化"""
        groups = {color: [] for color in self.COLOR_PRIORITY}

        for h in hissatsus:
            if h.color in groups:
                groups[h.color].append(h)
            else:
                logger.warning(f"Unknown color: {h.color} for hissatsu {h.name}")
                groups[self.COLOR_PRIORITY[0]].append(h)  # デフォルトは赤

        return groups

    def _layout_row_with_wrapping(self, color_groups: Dict[str, List[HissatsuInfo]]) -> List[List[HissatsuInfo]]:
        """
        必殺技を折り返しレイアウトに変換（1行に最大4枚）

        Returns:
            [[h1, h2, h3, h4], [h5, h6], ...]  # 各行の必殺技リスト
        """
        lines = []
        current_line = []

        for color in self.COLOR_PRIORITY:
            for hissatsu in color_groups[color]:
                if len(current_line) >= self.max_per_line:
                    lines.append(current_line)
                    current_line = []

                current_line.append(hissatsu)

        if current_line:
            lines.append(current_line)

        return lines

    def _calculate_max_width(self, all_row_lines: List[List[List[HissatsuInfo]]]) -> int:
        """全行の最大幅を計算"""
        max_width = 0

        for row_lines in all_row_lines:
            for line in row_lines:
                line_width = self.side_padding + (len(line) * self.hissatsu_width) + self.side_padding
                max_width = max(max_width, line_width)

        # 最小幅を確保
        return max(max_width, 800)

    def _calculate_total_height(self, all_row_lines: List[List[List[HissatsuInfo]]]) -> int:
        """全体の高さを計算"""
        total_height = self.header_height + self.row_gap

        for row_lines in all_row_lines:
            if not row_lines or all(len(line) == 0 for line in row_lines):
                continue  # 空行はスキップ

            # 行ラベル
            total_height += self.label_height

            # 各ラインの画像
            total_height += len(row_lines) * self.image_height

            # ライン間の隙間
            if len(row_lines) > 1:
                total_height += (len(row_lines) - 1) * self.line_gap

            # 行間の隙間
            total_height += self.row_gap

        return total_height

    def _draw_header(
        self,
        draw: ImageDraw,
        canvas_width: int,
        person1_name: str,
        person1_birthdate: str,
        person1_birthtime: str,
        person2_name: str,
        person2_birthdate: str,
        person2_birthtime: str
    ) -> int:
        """ヘッダーを描画"""
        # タイトル
        title = "My Dungeon Result - 2人の必殺技 -"
        bbox = draw.textbbox((0, 0), title, font=self.font_title)
        title_width = bbox[2] - bbox[0]
        title_x = (canvas_width - title_width) // 2
        draw.text((title_x, 25), title, fill=self.header_color, font=self.font_title)

        # 名前
        name_text = f"{person1_name or 'あなた'} × {person2_name or '相手'}"
        bbox = draw.textbbox((0, 0), name_text, font=self.font_large)
        name_width = bbox[2] - bbox[0]
        name_x = (canvas_width - name_width) // 2
        draw.text((name_x, 65), name_text, fill=self.text_color, font=self.font_large)

        # 日時
        datetime_text = f"{person1_birthdate} {person1_birthtime} × {person2_birthdate} {person2_birthtime}"
        bbox = draw.textbbox((0, 0), datetime_text, font=self.font_medium)
        datetime_width = bbox[2] - bbox[0]
        datetime_x = (canvas_width - datetime_width) // 2
        draw.text((datetime_x, 100), datetime_text, fill=self.text_color, font=self.font_medium)

        return self.header_height

    def _draw_hissatsu_row(
        self,
        canvas: Image,
        draw: ImageDraw,
        lines: List[List[HissatsuInfo]],
        start_y: int,
        label: str
    ) -> int:
        """必殺技の行を描画（折り返し対応）"""
        if not lines or all(len(line) == 0 for line in lines):
            return start_y  # 空行はスキップ

        current_y = start_y + self.row_gap

        # 行ラベルを描画
        draw.text((self.side_padding, current_y), label, fill=self.text_color, font=self.font_medium)
        current_y += self.label_height

        # 各ラインを描画
        for line in lines:
            current_x = self.side_padding

            for hissatsu in line:
                self._draw_hissatsu_image(canvas, current_x, current_y, hissatsu)
                current_x += self.hissatsu_width

            current_y += self.image_height + self.line_gap

        return current_y

    def _draw_hissatsu_image(
        self,
        canvas: Image,
        x: int,
        y: int,
        hissatsu: HissatsuInfo
    ):
        """必殺技画像を描画"""
        if hissatsu.image_path and os.path.exists(hissatsu.image_path):
            try:
                hissatsu_img = Image.open(hissatsu.image_path)
                hissatsu_img = hissatsu_img.resize((self.hissatsu_width, self.image_height), Image.Resampling.LANCZOS)
                canvas.paste(hissatsu_img, (x, y))
            except Exception as e:
                logger.warning(f"Failed to load hissatsu image: {hissatsu.image_path}, error: {e}")
                self._draw_placeholder(canvas, x, y, self.hissatsu_width, hissatsu.name)
        else:
            self._draw_placeholder(canvas, x, y, self.hissatsu_width, hissatsu.name)

    def _draw_placeholder(
        self,
        canvas: Image,
        x: int,
        y: int,
        width: int,
        text: str
    ):
        """画像がない場合のプレースホルダー"""
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([x, y, x + width, y + self.image_height], fill='lightgray', outline='gray')
        draw.text((x + 10, y + self.image_height // 2), f"No Image\n{text}", fill='black', font=self.font_small)
