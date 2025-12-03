"""
スクレイパー精度テスト
Webサイトから取得した生のテキストと、スクレイパーが抽出した数字が完全一致するかを検証

100パターンのランダムな生年月日・時刻でテストを実行
"""
import asyncio
import sys
import os
import random
import re
from datetime import datetime, timedelta
from typing import List, Tuple, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.scraper import DungeonScraper


class ScraperAccuracyTester:
    """スクレイパー精度テストクラス"""

    def __init__(self, num_tests: int = 100):
        self.num_tests = num_tests
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

    def extract_numbers_from_raw_text(self, raw_text: str) -> Set[int]:
        """
        生のテキストから数字を手動で抽出（スクレイパーとは独立した方法）

        Args:
            raw_text: Webサイトから取得した生のテキスト

        Returns:
            抽出した数字のセット
        """
        # 改行で分割して、各行を処理
        lines = raw_text.split('\n')
        numbers = set()

        for line in lines:
            line = line.strip()
            # 純粋な数字だけの行を探す
            if line.isdigit():
                num = int(line)
                # 1〜72の範囲の数字のみ
                if 1 <= num <= 72:
                    numbers.add(num)

        return numbers

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

            # Step 1: スクレイパーで数字と生テキストを取得
            scraped_numbers, raw_text = await self.scraper.scrape_numbers(
                birthdate, birthtime, return_raw_text=True
            )
            scraped_set = set(scraped_numbers)

            # Step 2: 生テキストから手動で数字を抽出
            expected_numbers = self.extract_numbers_from_raw_text(raw_text)

            print(f"  生テキストから抽出: {sorted(expected_numbers)}")
            print(f"  スクレイパー抽出: {sorted(scraped_set)}")

            # Step 3: 比較
            if scraped_set == expected_numbers:
                print(f"  ✅ 一致: {len(scraped_set)}個の数字が完全一致")
                return True
            else:
                # 詳細な差分を表示
                missing = expected_numbers - scraped_set
                extra = scraped_set - expected_numbers

                error_msg = f"❌ 不一致: {birthdate} {birthtime}\n"
                error_msg += f"   期待値: {sorted(expected_numbers)}\n"
                error_msg += f"   実際値: {sorted(scraped_set)}\n"

                if missing:
                    error_msg += f"   欠落している数字: {sorted(missing)}\n"
                if extra:
                    error_msg += f"   余分な数字: {sorted(extra)}\n"

                error_msg += f"\n   生テキスト（最初の500文字）:\n{raw_text[:500]}\n"

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
        print(f"スクレイパー精度テスト開始: {self.num_tests}パターン")
        print("=" * 80)
        print("\n【テスト内容】")
        print("- Webサイトの生テキストから手動で数字を抽出")
        print("- スクレイパーが抽出した数字と比較")
        print("- 完全一致するかを検証")
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
                print("-" * 80)

        print("\n" + "=" * 80)
        if self.failed == 0:
            print("🎉 全テスト成功！スクレイパーの精度に問題ありません。")
        else:
            print(f"⚠️  {self.failed}件のテストが失敗しました。")
            print("スクレイパーの正規表現パターンを見直す必要があります。")
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
    tester = ScraperAccuracyTester(num_tests=num_tests)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
