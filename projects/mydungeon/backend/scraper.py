import asyncio
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DungeonScraper:
    """外部サイトからデータを取得するスクレイパー"""

    def __init__(self):
        self.url = settings.TARGET_URL
        self.timeout = settings.SCRAPING_TIMEOUT

    async def scrape_numbers(self, birthdate: str, birthtime: str) -> List[int]:
        """
        生年月日と時刻を入力して数字を取得

        Args:
            birthdate: 生年月日 (YYYY-MM-DD)
            birthtime: 時刻 (HH:MM)

        Returns:
            取得した数字のリスト
        """
        # 日付と時刻を分解（先頭ゼロを削除）
        year, month, day = birthdate.split('-')
        month = str(int(month))  # 先頭ゼロ削除
        day = str(int(day))  # 先頭ゼロ削除
        hour, minute = birthtime.split(':')
        hour = str(int(hour))  # 先頭ゼロ削除
        minute = str(int(minute))  # 先頭ゼロ削除

        async with async_playwright() as p:
            # Codespaces環境ではXServerが無いため、常にヘッドレスモードを使用
            browser = await p.chromium.launch(headless=True)
            # 日本のタイムゾーンとロケールを設定
            context = await browser.new_context(
                timezone_id='Asia/Tokyo',
                locale='ja-JP'
            )
            page = await context.new_page()

            try:
                logger.info(f"Accessing {self.url}")
                await page.goto(self.url, timeout=self.timeout)

                # ページの読み込み待機
                await page.wait_for_selector('fieldset[name="dateFields"]', timeout=self.timeout)

                # 生年月日の入力
                logger.info(f"Selecting birthdate: {year}/{month}/{day}")

                # 年の選択
                await page.select_option('fieldset[name="dateFields"] select:nth-of-type(1)', year)
                await asyncio.sleep(0.5)

                # 月の選択
                await page.select_option('fieldset[name="dateFields"] select:nth-of-type(2)', month)
                await asyncio.sleep(0.5)

                # 日の選択
                await page.select_option('fieldset[name="dateFields"] select:nth-of-type(3)', day)
                await asyncio.sleep(0.5)

                # 時刻の入力
                logger.info(f"Selecting birthtime: {hour}:{minute}")

                # 時の選択
                await page.select_option('fieldset[name="timeFields"] select:nth-of-type(1)', hour)
                await asyncio.sleep(0.5)

                # 分の選択
                await page.select_option('fieldset[name="timeFields"] select:nth-of-type(2)', minute)
                await asyncio.sleep(0.5)

                # スクリーンショット（デバッグ用）
                if not settings.HEADLESS:
                    await page.screenshot(path=os.path.join(settings.OUTPUT_DIR, 'before_submit.png'))

                # ボタンをクリック
                logger.info("Clicking submit button")
                await page.click('button.button')

                # 結果の表示を待つ（数秒待機）
                await asyncio.sleep(3)

                # スクリーンショット（結果確認用）
                if not settings.HEADLESS:
                    await page.screenshot(path=os.path.join(settings.OUTPUT_DIR, 'after_submit.png'))

                # 結果が表示される要素を探す
                # 動的に生成される可能性が高いので、複数のパターンを試す
                numbers = []

                # パターン1: テーブル要素を探す
                try:
                    await page.wait_for_selector('table', timeout=5000)
                    # テーブル内の数字を抽出
                    table_text = await page.inner_text('table')
                    logger.info(f"Table text found: {table_text[:200]}")
                    # 数字を抽出（1〜60の範囲）
                    found_numbers = re.findall(r'\b([1-5]?[0-9]|60)\b', table_text)
                    numbers = [int(n) for n in found_numbers if 1 <= int(n) <= 60]
                except PlaywrightTimeout:
                    logger.warning("Table not found, trying other patterns")

                # パターン2: 結果が表示されるdiv要素を探す
                if not numbers:
                    try:
                        await page.wait_for_selector('#app section:not(#data-input)', timeout=5000)
                        result_section = await page.query_selector('#app section:not(#data-input)')
                        if result_section:
                            result_text = await result_section.inner_text()
                            logger.info(f"Result section found: {result_text[:200]}")
                            found_numbers = re.findall(r'\b([1-5]?[0-9]|60)\b', result_text)
                            numbers = [int(n) for n in found_numbers if 1 <= int(n) <= 60]
                    except PlaywrightTimeout:
                        logger.warning("Result section not found")

                # パターン3: ページ全体のテキストから抽出
                if not numbers:
                    logger.info("Trying to extract from full page content")
                    page_content = await page.content()

                    # HTMLをファイルに保存（デバッグ用）
                    with open(os.path.join(settings.OUTPUT_DIR, 'page_content.html'), 'w', encoding='utf-8') as f:
                        f.write(page_content)

                    # テキストコンテンツ全体から数字を抽出
                    body_text = await page.inner_text('body')
                    logger.info(f"Body text: {body_text[:500]}")

                    # 1〜60の範囲の数字を抽出
                    found_numbers = re.findall(r'\b([1-5]?[0-9]|60)\b', body_text)
                    # 重複を除去せず、順番に並べる
                    numbers = [int(n) for n in found_numbers if 1 <= int(n) <= 60]

                    # 明らかに関係ない数字（年月日など）を除外
                    # 生年月日と時刻に含まれる数字を除外
                    exclude_numbers = [int(year), int(month), int(day), int(hour), int(minute)]
                    numbers = [n for n in numbers if n not in exclude_numbers]

                # 重複を除去（順序は保持）
                seen = set()
                unique_numbers = []
                for n in numbers:
                    if n not in seen:
                        seen.add(n)
                        unique_numbers.append(n)

                numbers = unique_numbers

                logger.info(f"Extracted numbers: {numbers}")

                if not numbers:
                    logger.error("No numbers found. Check the output directory for screenshots and HTML.")

                return numbers

            except Exception as e:
                logger.error(f"Scraping error: {str(e)}")
                # エラー時もスクリーンショットを保存
                try:
                    await page.screenshot(path=os.path.join(settings.OUTPUT_DIR, 'error.png'))
                except:
                    pass
                raise
            finally:
                await context.close()
                await browser.close()


# テスト用
async def main():
    scraper = DungeonScraper()

    # テストデータ
    test_birthdate = "1990-01-01"
    test_birthtime = "12:30"

    logger.info(f"Testing scraper with {test_birthdate} {test_birthtime}")
    numbers = await scraper.scrape_numbers(test_birthdate, test_birthtime)

    print(f"\n取得した数字: {numbers}")
    print(f"数字の個数: {len(numbers)}")

if __name__ == "__main__":
    asyncio.run(main())
