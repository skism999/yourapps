import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_processor import DataProcessor


class TestDataProcessor:
    """DataProcessorのテスト"""

    @pytest.fixture
    def processor(self):
        """データプロセッサーのインスタンスを作成"""
        return DataProcessor()

    def test_load_csv_data(self, processor):
        """CSVファイルの読み込みテスト"""
        assert processor.item_df is not None
        assert processor.hissatsu_df is not None
        assert len(processor.item_df) > 0
        assert len(processor.hissatsu_df) > 0

        # 列名の確認
        expected_item_columns = ['No', 'アイテム名', '対No', '対アイテム名', '必殺No', '必殺技名', '色', '動き方', '説明', 'ON', 'OFF']
        assert list(processor.item_df.columns) == expected_item_columns

        expected_hissatsu_columns = ['必殺No', '必殺技名', '色', '意味', '動き方', '基本姿勢', '才能', '特性', 'アドバイス', 'ON', 'OFF']
        assert list(processor.hissatsu_df.columns) == expected_hissatsu_columns

        print(f"\n✓ Loaded {len(processor.item_df)} items")
        print(f"✓ Loaded {len(processor.hissatsu_df)} hissatsuwaza")

    def test_get_items_by_numbers(self, processor):
        """数字からアイテム情報を取得するテスト"""
        # 1991年9月16日13時50分の結果
        test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]

        items = processor.get_items_by_numbers(test_numbers)

        # 全ての数字に対応するアイテムが取得できたか確認
        assert len(items) == len(test_numbers)

        # 各アイテムの検証
        for item in items:
            assert item.no in test_numbers
            assert item.name is not None
            assert item.color is not None
            assert item.movement is not None
            # 画像パスが設定されているか（空文字の場合もある）
            assert isinstance(item.image_path, str)

        # 特定のアイテムの検証
        item_1 = next(item for item in items if item.no == 1)
        assert item_1.name == "タレント"
        assert item_1.pair_no == 8
        assert item_1.hissatsu_no == 1

        print(f"\n✓ Retrieved {len(items)} items")
        print(f"✓ Sample: No.{item_1.no} - {item_1.name}")

    def test_detect_hissatsuwaza(self, processor):
        """必殺技判定のテスト"""
        # No.6とNo.59はペアなので、必殺No.6が発動するはず
        test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]

        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        # 必殺技が発動しているか確認
        assert len(hissatsus) > 0

        # No.6とNo.59のペアで必殺No.6「エロ」が発動しているか
        hissatsu_6 = next((h for h in hissatsus if h.hissatsu_no == 6), None)
        assert hissatsu_6 is not None
        assert hissatsu_6.name == "エロ"

        print(f"\n✓ Detected {len(hissatsus)} hissatsuwaza")
        for h in hissatsus:
            print(f"  - 必殺No.{h.hissatsu_no}: {h.name}")

    def test_no_hissatsuwaza(self, processor):
        """ペアがない場合、必殺技が発動しないテスト"""
        # ペアにならない数字のみ
        test_numbers = [1, 2, 3, 5, 7, 9]

        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        # 必殺技が発動していないことを確認
        assert len(hissatsus) == 0

        print("\n✓ No hissatsuwaza activated (expected)")

    def test_multiple_hissatsuwaza(self, processor):
        """複数の必殺技が発動する場合のテスト"""
        # No.1とNo.8のペア（必殺No.1）
        # No.6とNo.59のペア（必殺No.6）
        test_numbers = [1, 6, 8, 59]

        hissatsus = processor.detect_hissatsuwaza(test_numbers)

        # 2つの必殺技が発動しているか確認
        assert len(hissatsus) == 2

        hissatsu_nos = {h.hissatsu_no for h in hissatsus}
        assert 1 in hissatsu_nos  # 天才クリエイター
        assert 6 in hissatsu_nos  # エロ

        print(f"\n✓ Multiple hissatsuwaza activated: {len(hissatsus)}")
        for h in hissatsus:
            print(f"  - 必殺No.{h.hissatsu_no}: {h.name}")

    def test_image_path_resolution(self, processor):
        """画像パスの解決テスト"""
        test_numbers = [1, 4, 6]

        items = processor.get_items_by_numbers(test_numbers)

        for item in items:
            # 画像パスが存在するか、または空文字列であることを確認
            assert isinstance(item.image_path, str)

            if item.image_path:
                # 画像ファイルが実際に存在するか確認
                assert os.path.exists(item.image_path), f"Image not found: {item.image_path}"
                print(f"✓ No.{item.no}: {os.path.basename(item.image_path)}")


# スタンドアロン実行用
if __name__ == "__main__":
    processor = DataProcessor()

    print("=" * 50)
    print("データプロセッサーテスト")
    print("=" * 50)

    # テスト1: CSV読み込み
    print("\n[Test 1] CSV読み込み")
    print(f"  アイテム数: {len(processor.item_df)}")
    print(f"  必殺技数: {len(processor.hissatsu_df)}")

    # テスト2: アイテム取得
    print("\n[Test 2] アイテム取得")
    test_numbers = [1, 4, 6, 11, 12, 33, 36, 38, 40, 41, 48, 53, 54, 59, 60]
    items = processor.get_items_by_numbers(test_numbers)
    print(f"  取得したアイテム数: {len(items)}")

    # テスト3: 必殺技判定
    print("\n[Test 3] 必殺技判定")
    hissatsus = processor.detect_hissatsuwaza(test_numbers)
    print(f"  発動した必殺技数: {len(hissatsus)}")
    for h in hissatsus:
        print(f"    - 必殺No.{h.hissatsu_no}: {h.name}")

    # テスト4: 複数必殺技
    print("\n[Test 4] 複数必殺技発動")
    test_numbers_multi = [1, 6, 8, 59]
    hissatsus_multi = processor.detect_hissatsuwaza(test_numbers_multi)
    print(f"  発動した必殺技数: {len(hissatsus_multi)}")
    for h in hissatsus_multi:
        print(f"    - 必殺No.{h.hissatsu_no}: {h.name}")

    print("\n" + "=" * 50)
    print("全テスト完了")
    print("=" * 50)
