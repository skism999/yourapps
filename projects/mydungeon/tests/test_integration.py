import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scraper import DungeonScraper
from backend.data_processor import DataProcessor


class TestIntegration:
    """スクレイピングからデータ処理までの統合テスト"""

    @pytest.fixture
    def scraper(self):
        """スクレイパーのインスタンス"""
        return DungeonScraper()

    @pytest.fixture
    def processor(self):
        """データプロセッサーのインスタンス"""
        return DataProcessor()

    @pytest.mark.asyncio
    async def test_full_flow_1991_09_16(self, scraper, processor):
        """
        1991年9月16日13時50分の完全なフローテスト
        スクレイピング → アイテム取得 → 必殺技判定
        """
        birthdate = "1991-09-16"
        birthtime = "13:50"

        # Step 1: スクレイピング
        print(f"\n[Step 1] スクレイピング実行: {birthdate} {birthtime}")
        numbers = await scraper.scrape_numbers(birthdate, birthtime)

        print(f"取得した数字: {numbers}")
        print(f"数字の個数: {len(numbers)}")

        assert numbers is not None
        assert len(numbers) > 0

        # Step 2: アイテム情報の取得
        print("\n[Step 2] アイテム情報の取得")
        items = processor.get_items_by_numbers(numbers)

        print(f"取得したアイテム数: {len(items)}")
        assert len(items) == len(numbers)

        # アイテム情報の表示
        print("\n取得したアイテム:")
        for item in items:
            print(f"  No.{item.no}: {item.name}")
            print(f"    色: {item.color} | 動き方: {item.movement}")
            print(f"    対No: {item.pair_no} ({item.pair_name})")
            if item.hissatsu_no:
                print(f"    必殺No: {item.hissatsu_no} ({item.hissatsu_name})")
            if item.image_path:
                print(f"    画像: {os.path.basename(item.image_path)}")
                # 画像ファイルが存在するか確認
                assert os.path.exists(item.image_path), f"画像が見つかりません: {item.image_path}"

        # Step 3: 必殺技判定
        print("\n[Step 3] 必殺技判定")
        hissatsus = processor.detect_hissatsuwaza(numbers)

        print(f"発動した必殺技数: {len(hissatsus)}")

        if len(hissatsus) > 0:
            print("\n発動した必殺技:")
            for h in hissatsus:
                print(f"  必殺No.{h.hissatsu_no}: {h.name}")
                print(f"    色: {h.color}")
                print(f"    意味: {h.meaning}")
                print(f"    基本姿勢: {h.basic_posture}")
                if h.image_path:
                    print(f"    画像: {os.path.basename(h.image_path)}")
                    # 画像ファイルが存在するか確認
                    assert os.path.exists(h.image_path), f"必殺技画像が見つかりません: {h.image_path}"
        else:
            print("  (必殺技は発動していません)")

        # Step 4: データの整合性チェック
        print("\n[Step 4] データ整合性チェック")

        # 各アイテムについて、対Noが数字リストに含まれている場合、必殺技が発動しているか確認
        number_set = set(numbers)
        expected_hissatsus = set()

        for item in items:
            if item.pair_no and item.pair_no in number_set and item.hissatsu_no:
                expected_hissatsus.add(item.hissatsu_no)

        actual_hissatsus = {h.hissatsu_no for h in hissatsus}

        print(f"期待される必殺技No: {sorted(expected_hissatsus)}")
        print(f"実際の必殺技No: {sorted(actual_hissatsus)}")

        assert expected_hissatsus == actual_hissatsus, \
            f"必殺技の判定に不一致があります。期待: {expected_hissatsus}, 実際: {actual_hissatsus}"

        print("\n✓ 全ての検証に成功しました")

    @pytest.mark.asyncio
    async def test_item_pair_detection(self, scraper, processor):
        """
        アイテムのペア検出テスト
        """
        birthdate = "1991-09-16"
        birthtime = "13:50"

        numbers = await scraper.scrape_numbers(birthdate, birthtime)
        items = processor.get_items_by_numbers(numbers)

        number_set = set(numbers)
        pairs_found = []

        for item in items:
            if item.pair_no and item.pair_no in number_set:
                pairs_found.append((item.no, item.pair_no, item.hissatsu_no))

        print(f"\n見つかったペア:")
        for no, pair_no, hissatsu_no in pairs_found:
            print(f"  No.{no} ←→ No.{pair_no} → 必殺No.{hissatsu_no}")

        # ペアが見つかっている場合、必殺技も発動しているはず
        if len(pairs_found) > 0:
            hissatsus = processor.detect_hissatsuwaza(numbers)
            assert len(hissatsus) == len(set(h[2] for h in pairs_found))

    @pytest.mark.asyncio
    async def test_all_images_exist(self, scraper, processor):
        """
        取得した全ての画像ファイルが存在するかテスト
        """
        birthdate = "1991-09-16"
        birthtime = "13:50"

        numbers = await scraper.scrape_numbers(birthdate, birthtime)
        items = processor.get_items_by_numbers(numbers)
        hissatsus = processor.detect_hissatsuwaza(numbers)

        print("\n画像ファイルチェック:")

        # アイテム画像のチェック
        missing_images = []
        for item in items:
            if item.image_path:
                if os.path.exists(item.image_path):
                    print(f"  ✓ No.{item.no}: {os.path.basename(item.image_path)}")
                else:
                    missing_images.append(f"No.{item.no}: {item.image_path}")
                    print(f"  ✗ No.{item.no}: {os.path.basename(item.image_path)} (見つかりません)")
            else:
                print(f"  - No.{item.no}: 画像パスが設定されていません")

        # 必殺技画像のチェック
        for h in hissatsus:
            if h.image_path:
                if os.path.exists(h.image_path):
                    print(f"  ✓ 必殺No.{h.hissatsu_no}: {os.path.basename(h.image_path)}")
                else:
                    missing_images.append(f"必殺No.{h.hissatsu_no}: {h.image_path}")
                    print(f"  ✗ 必殺No.{h.hissatsu_no}: {os.path.basename(h.image_path)} (見つかりません)")
            else:
                print(f"  - 必殺No.{h.hissatsu_no}: 画像パスが設定されていません")

        if missing_images:
            print(f"\n見つからない画像: {len(missing_images)}個")
            for img in missing_images:
                print(f"  - {img}")
        else:
            print("\n✓ 全ての画像ファイルが存在します")

        # 画像が見つからない場合は警告のみ（エラーにはしない）
        # 実際の運用では画像が揃っている必要がある


# スタンドアロン実行用
if __name__ == "__main__":
    async def main():
        scraper = DungeonScraper()
        processor = DataProcessor()

        birthdate = "1991-09-16"
        birthtime = "13:50"

        print("=" * 70)
        print(f"統合テスト: {birthdate} {birthtime}")
        print("=" * 70)

        # スクレイピング
        print("\n[1] スクレイピング実行中...")
        numbers = await scraper.scrape_numbers(birthdate, birthtime)
        print(f"✓ 取得した数字: {numbers} ({len(numbers)}個)")

        # アイテム取得
        print("\n[2] アイテム情報取得中...")
        items = processor.get_items_by_numbers(numbers)
        print(f"✓ 取得したアイテム数: {len(items)}")

        print("\nアイテム一覧:")
        for item in items:
            status = "✓" if item.image_path and os.path.exists(item.image_path) else "✗"
            print(f"  {status} No.{item.no:2d}: {item.name:15s} (対No.{item.pair_no or 'なし'})")

        # 必殺技判定
        print("\n[3] 必殺技判定中...")
        hissatsus = processor.detect_hissatsuwaza(numbers)
        print(f"✓ 発動した必殺技数: {len(hissatsus)}")

        if hissatsus:
            print("\n必殺技一覧:")
            for h in hissatsus:
                status = "✓" if h.image_path and os.path.exists(h.image_path) else "✗"
                print(f"  {status} 必殺No.{h.hissatsu_no:2d}: {h.name}")
                print(f"      {h.meaning}")

        # ペア検出
        print("\n[4] ペア検出中...")
        number_set = set(numbers)
        pairs = []
        for item in items:
            if item.pair_no and item.pair_no in number_set:
                pairs.append((item.no, item.pair_no, item.hissatsu_no, item.hissatsu_name))

        if pairs:
            print(f"✓ 見つかったペア: {len(pairs)}組")
            for no, pair_no, hissatsu_no, hissatsu_name in pairs:
                print(f"  No.{no} ←→ No.{pair_no} → 必殺No.{hissatsu_no} ({hissatsu_name})")
        else:
            print("  ペアは見つかりませんでした")

        print("\n" + "=" * 70)
        print("統合テスト完了")
        print("=" * 70)

    asyncio.run(main())
