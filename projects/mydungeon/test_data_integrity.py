"""
データ整合性テスト
スクレイピングで取得した数字と最終出力される数字が一致するかを検証

100パターンのランダムな生年月日・時刻でテストを実行
"""
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.dungeon_service import DungeonService
from backend.scraper import DungeonScraper


class DataIntegrityTester:
    """データ整合性テストクラス"""

    def __init__(self, num_tests: int = 100):
        self.num_tests = num_tests
        self.service = DungeonService()
        self.scraper = DungeonScraper()
        self.passed = 0
        self.failed = 0
        self.errors = []

    def generate_random_datetime(self) -> Tuple[str, str]:
        """
        ランダムな生年月日と時刻を生成

        Returns:
            (birthdate, birthtime): YYYY-MM-DD, HH:MM形式
        """
        # 1950年1月1日から2024年12月31日までのランダムな日付
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2024, 12, 31)

        # ランダムな日数を加算
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)

        # ランダムな時刻（0-23時、0-59分）
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)

        birthdate = random_date.strftime("%Y-%m-%d")
        birthtime = f"{random_hour:02d}:{random_minute:02d}"

        return birthdate, birthtime

    async def test_single_pattern(self, test_num: int, birthdate: str, birthtime: str) -> bool:
        """
        単一パターンのテスト実行

        Args:
            test_num: テスト番号
            birthdate: 生年月日 (YYYY-MM-DD)
            birthtime: 時刻 (HH:MM)

        Returns:
            bool: テスト成功ならTrue
        """
        try:
            print(f"\n[テスト {test_num}/{self.num_tests}] {birthdate} {birthtime}")

            # Step 1: スクレイピングで数字を取得
            scraped_numbers = await self.scraper.scrape_numbers(birthdate, birthtime)
            print(f"  スクレイピング結果: {scraped_numbers}")

            # Step 2: DungeonServiceで最終結果を取得
            result = await self.service.get_result_summary(birthdate, birthtime, name=None)
            output_numbers = result.get('numbers', [])
            print(f"  最終出力結果: {output_numbers}")

            # Step 3: 数字の一致を確認
            if scraped_numbers == output_numbers:
                print(f"  ✅ 一致: {len(scraped_numbers)}個の数字が完全一致")
                return True
            else:
                # 詳細な差分を表示
                scraped_set = set(scraped_numbers)
                output_set = set(output_numbers)

                missing_in_output = scraped_set - output_set
                extra_in_output = output_set - scraped_set

                error_msg = f"❌ 不一致: {birthdate} {birthtime}\n"
                error_msg += f"   スクレイピング: {scraped_numbers}\n"
                error_msg += f"   最終出力: {output_numbers}\n"

                if missing_in_output:
                    error_msg += f"   出力に欠落: {missing_in_output}\n"
                if extra_in_output:
                    error_msg += f"   出力に余剰: {extra_in_output}\n"

                print(error_msg)
                self.errors.append(error_msg)
                return False

        except Exception as e:
            error_msg = f"❌ エラー発生: {birthdate} {birthtime}\n   {str(e)}"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    async def run_all_tests(self):
        """全テストを実行"""
        print("=" * 80)
        print(f"データ整合性テスト開始: {self.num_tests}パターン")
        print("=" * 80)

        start_time = datetime.now()

        for i in range(1, self.num_tests + 1):
            # ランダムな生年月日・時刻を生成
            birthdate, birthtime = self.generate_random_datetime()

            # テスト実行
            success = await self.test_single_pattern(i, birthdate, birthtime)

            if success:
                self.passed += 1
            else:
                self.failed += 1

            # 10件ごとに進捗表示
            if i % 10 == 0:
                print(f"\n--- 進捗: {i}/{self.num_tests} 完了 (成功: {self.passed}, 失敗: {self.failed}) ---")

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # 結果サマリー
        self.print_summary(elapsed_time)

    def print_summary(self, elapsed_time: float):
        """テスト結果のサマリーを表示"""
        print("\n" + "=" * 80)
        print("テスト結果サマリー")
        print("=" * 80)
        print(f"総テスト数: {self.num_tests}")
        print(f"成功: {self.passed} ({self.passed/self.num_tests*100:.1f}%)")
        print(f"失敗: {self.failed} ({self.failed/self.num_tests*100:.1f}%)")
        print(f"実行時間: {elapsed_time:.1f}秒 (平均: {elapsed_time/self.num_tests:.2f}秒/件)")

        if self.failed > 0:
            print("\n" + "=" * 80)
            print("失敗したテストの詳細")
            print("=" * 80)
            for error in self.errors:
                print(error)

        print("\n" + "=" * 80)
        if self.failed == 0:
            print("🎉 全テスト成功！データ整合性に問題ありません。")
        else:
            print(f"⚠️  {self.failed}件のテストが失敗しました。上記の詳細を確認してください。")
        print("=" * 80)


async def main():
    """メイン関数"""
    # テスト件数を指定（デフォルト: 100）
    num_tests = 100

    # コマンドライン引数でテスト数を変更可能
    if len(sys.argv) > 1:
        try:
            num_tests = int(sys.argv[1])
            print(f"テスト数を{num_tests}件に設定しました")
        except ValueError:
            print(f"警告: 無効な引数 '{sys.argv[1]}'。デフォルトの100件でテストを実行します。")

    # テスト実行
    tester = DataIntegrityTester(num_tests=num_tests)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
