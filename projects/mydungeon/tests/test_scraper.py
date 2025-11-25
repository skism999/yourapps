import pytest
import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scraper import DungeonScraper


class TestDungeonScraper:
    """DungeonScraperのテスト"""

    @pytest.fixture
    def scraper(self):
        """スクレイパーのインスタンスを作成"""
        return DungeonScraper()

    @pytest.mark.asyncio
    async def test_scrape_numbers_1991_09_16(self, scraper):
        """
        1991年9月16日13時50分のスクレイピングテスト
        """
        birthdate = "1991-09-16"
        birthtime = "13:50"

        # スクレイピング実行
        numbers = await scraper.scrape_numbers(birthdate, birthtime)

        # 検証
        assert numbers is not None, "数字リストがNoneです"
        assert isinstance(numbers, list), "数字リストがリスト型ではありません"
        assert len(numbers) > 0, "数字が取得できていません"

        # 全ての要素が整数であることを確認
        for num in numbers:
            assert isinstance(num, int), f"数字 {num} が整数型ではありません"

        # 全ての数字が1〜60の範囲内であることを確認
        for num in numbers:
            assert 1 <= num <= 60, f"数字 {num} が範囲外です（1〜60の範囲内である必要があります）"

        # 重複がないことを確認
        assert len(numbers) == len(set(numbers)), "数字に重複があります"

        # 結果を出力
        print(f"\n取得した数字: {numbers}")
        print(f"数字の個数: {len(numbers)}")

    @pytest.mark.asyncio
    async def test_scrape_numbers_format(self, scraper):
        """
        取得した数字の形式テスト
        """
        birthdate = "1991-09-16"
        birthtime = "13:50"

        numbers = await scraper.scrape_numbers(birthdate, birthtime)

        # 期待される個数の範囲（15〜25個）
        assert 15 <= len(numbers) <= 25, f"数字の個数が範囲外です: {len(numbers)}個（期待: 15〜25個）"

    @pytest.mark.asyncio
    async def test_scrape_numbers_different_date(self, scraper):
        """
        異なる日付でのスクレイピングテスト
        """
        birthdate = "1990-01-01"
        birthtime = "12:30"

        numbers = await scraper.scrape_numbers(birthdate, birthtime)

        assert numbers is not None
        assert len(numbers) > 0
        print(f"\n[1990-01-01 12:30] 取得した数字: {numbers}")

    @pytest.mark.asyncio
    async def test_scrape_numbers_edge_cases(self, scraper):
        """
        エッジケースのテスト
        """
        test_cases = [
            ("2000-12-31", "23:59"),  # 年末の深夜
            ("1990-01-01", "00:00"),  # 年始の深夜0時
            ("1995-06-15", "12:00"),  # 正午
        ]

        for birthdate, birthtime in test_cases:
            numbers = await scraper.scrape_numbers(birthdate, birthtime)
            assert numbers is not None, f"[{birthdate} {birthtime}] 数字が取得できませんでした"
            assert len(numbers) > 0, f"[{birthdate} {birthtime}] 数字が空です"
            print(f"\n[{birthdate} {birthtime}] 取得した数字: {numbers} ({len(numbers)}個)")


# スタンドアロン実行用
if __name__ == "__main__":
    # 1991年9月16日13時50分のテストを実行
    async def main():
        scraper = DungeonScraper()
        birthdate = "1991-09-16"
        birthtime = "13:50"

        print(f"スクレイピングテスト: {birthdate} {birthtime}")
        print("=" * 50)

        numbers = await scraper.scrape_numbers(birthdate, birthtime)

        print(f"\n取得した数字: {numbers}")
        print(f"数字の個数: {len(numbers)}")

        # 検証結果
        print("\n検証結果:")
        print(f"  ✓ 数字が取得できました: {len(numbers)}個")
        print(f"  ✓ 全て整数型: {all(isinstance(n, int) for n in numbers)}")
        print(f"  ✓ 範囲内(1〜60): {all(1 <= n <= 60 for n in numbers)}")
        print(f"  ✓ 重複なし: {len(numbers) == len(set(numbers))}")
        print(f"  ✓ 期待個数範囲(15〜25): {15 <= len(numbers) <= 25}")

    asyncio.run(main())
