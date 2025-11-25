import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_processor import DataProcessor
from backend.image_processor import ImageProcessor
from PIL import Image


class TestImageProcessor:
    """ImageProcessorのテスト"""

    @pytest.fixture
    def processor(self):
        """データプロセッサーのインスタンス"""
        return DataProcessor()

    @pytest.fixture
    def img_processor(self):
        """画像プロセッサーのインスタンス"""
        return ImageProcessor()

    def test_create_result_image(self, processor, img_processor):
        """画像生成のテスト"""
        # 1991年9月16日13時50分のテストデータ
        test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]
        birthdate = "1991-09-16"
        birthtime = "13:50"

        items = processor.get_items_by_numbers(test_numbers)
        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        # 画像生成
        output_path = img_processor.create_result_image(items, hissatsus, birthdate, birthtime)

        # 検証
        assert output_path is not None
        assert os.path.exists(output_path), "画像ファイルが生成されていません"

        # 画像を読み込んで検証
        img = Image.open(output_path)
        assert img.size[0] > 0, "画像の幅が0です"
        assert img.size[1] > 0, "画像の高さが0です"

        # ファイルサイズ確認
        file_size = os.path.getsize(output_path)
        assert file_size > 0, "ファイルサイズが0です"

        print(f"\n✓ 画像生成成功")
        print(f"  パス: {output_path}")
        print(f"  サイズ: {img.size}")
        print(f"  ファイルサイズ: {file_size / 1024:.1f} KB")

    def test_image_dimensions(self, processor, img_processor):
        """画像のサイズが正しいかテスト"""
        test_numbers = [1, 4, 6]
        items = processor.get_items_by_numbers(test_numbers)
        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        output_path = img_processor.create_result_image(items, hissatsus)
        img = Image.open(output_path)

        # 最小サイズの確認
        assert img.size[0] >= 800, "画像の幅が小さすぎます"
        assert img.size[1] >= 400, "画像の高さが小さすぎます"

        print(f"\n✓ 画像サイズ: {img.size}")

    def test_multiple_hissatsus(self, processor, img_processor):
        """複数の必殺技がある場合のテスト"""
        # No.1とNo.8、No.6とNo.59のペアを含む
        test_numbers = [1, 6, 8, 59]
        items = processor.get_items_by_numbers(test_numbers)
        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        assert len(hissatsus) == 2, "必殺技が2つ発動するはず"

        output_path = img_processor.create_result_image(items, hissatsus)

        assert os.path.exists(output_path)
        img = Image.open(output_path)

        print(f"\n✓ 複数必殺技の画像生成成功")
        print(f"  必殺技数: {len(hissatsus)}")
        print(f"  アイテム数: {len(items)}")
        print(f"  画像サイズ: {img.size}")

    def test_no_hissatsu(self, processor, img_processor):
        """必殺技がない場合のテスト"""
        # ペアにならない数字
        test_numbers = [1, 2, 3, 5]
        items = processor.get_items_by_numbers(test_numbers)
        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        assert len(hissatsus) == 0, "必殺技は発動しないはず"

        output_path = img_processor.create_result_image(items, hissatsus)

        assert os.path.exists(output_path)
        img = Image.open(output_path)

        print(f"\n✓ 必殺技なしの画像生成成功")
        print(f"  アイテム数: {len(items)}")
        print(f"  画像サイズ: {img.size}")

    def test_layout_order(self, processor, img_processor):
        """レイアウト順序のテスト"""
        test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]

        items = processor.get_items_by_numbers(test_numbers)
        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        # レイアウトマネージャーのインポート
        from backend.layout_manager import LayoutManager

        sorted_hissatsus, sorted_items = LayoutManager.sort_items(items, hissatsus)

        print(f"\n✓ レイアウト順序:")
        print(f"  必殺技: {[h.hissatsu_no for h in sorted_hissatsus]}")
        print(f"  アイテム（色系統順）:")

        current_group = None
        for item in sorted_items:
            group = LayoutManager.get_color_group(item.color)
            if group != current_group:
                print(f"    [{group}]", end=" ")
                current_group = group
            print(f"No.{item.no}", end=" ")
        print()

        # 画像生成
        output_path = img_processor.create_result_image(items, hissatsus)
        assert os.path.exists(output_path)


# スタンドアロン実行用
if __name__ == "__main__":
    processor = DataProcessor()
    img_processor = ImageProcessor()

    print("=" * 70)
    print("画像プロセッサーテスト")
    print("=" * 70)

    # テスト1: 基本的な画像生成
    print("\n[Test 1] 基本的な画像生成")
    test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]
    items = processor.get_items_by_numbers(test_numbers)
    hissatsus = processor.detect_hissatsuwaza(test_numbers)
    output_path = img_processor.create_result_image(items, hissatsus, "1991-09-16", "13:50")
    print(f"  生成: {output_path}")

    # テスト2: 複数必殺技
    print("\n[Test 2] 複数必殺技")
    test_numbers_multi = [1, 6, 8, 59]
    items_multi = processor.get_items_by_numbers(test_numbers_multi)
    hissatsus_multi = processor.detect_hissatsuwaza(test_numbers_multi)
    output_path_multi = img_processor.create_result_image(items_multi, hissatsus_multi)
    print(f"  生成: {output_path_multi}")
    print(f"  必殺技数: {len(hissatsus_multi)}")

    # テスト3: 必殺技なし
    print("\n[Test 3] 必殺技なし")
    test_numbers_no = [1, 2, 3, 5]
    items_no = processor.get_items_by_numbers(test_numbers_no)
    hissatsus_no = processor.detect_hissatsuwaza(test_numbers_no)
    output_path_no = img_processor.create_result_image(items_no, hissatsus_no)
    print(f"  生成: {output_path_no}")
    print(f"  必殺技数: {len(hissatsus_no)}")

    print("\n" + "=" * 70)
    print("全テスト完了")
    print("=" * 70)
