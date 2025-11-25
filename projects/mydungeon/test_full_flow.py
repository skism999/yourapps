"""
完全なフローテスト: DungeonServiceを使用
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.dungeon_service import DungeonService


async def main():
    birthdate = "1992-01-10"
    birthtime = "10:30"
    name = "yukino"

    print("=" * 70)
    print(f"完全フローテスト: {name} - {birthdate} {birthtime}")
    print("=" * 70)

    # DungeonServiceを使用して完全な結果を生成
    print("\n結果生成中...")
    service = DungeonService()

    result = await service.get_result_summary(birthdate, birthtime, name)

    # 結果の表示
    print(f"\n✓ 完了しました！")
    print(f"\n名前: {result['name']}")
    print(f"生年月日: {result['birthdate']} {result['birthtime']}")
    print(f"\n取得した数字: {result['numbers']}")
    print(f"  数字の個数: {len(result['numbers'])}")

    print(f"\nアイテム一覧: {result['item_count']}個")
    for item in result['items']:
        hissatsu_mark = "★" if item['has_hissatsu'] else " "
        print(f"  {hissatsu_mark} No.{item['no']:2d}: {item['name']:15s} ({item['color']})")

    print(f"\n必殺技一覧: {result['hissatsu_count']}個")
    if result['hissatsus']:
        for h in result['hissatsus']:
            print(f"  必殺No.{h['hissatsu_no']:2d}: {h['name']:20s} ({h['color']})")
            print(f"    {h['meaning']}")
    else:
        print("  (必殺技は発動していません)")

    print(f"\n生成された画像: {result['image_path']}")
    if os.path.exists(result['image_path']):
        file_size = os.path.getsize(result['image_path']) / 1024
        print(f"  ファイルサイズ: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✓ 全てのステップが完了しました")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
