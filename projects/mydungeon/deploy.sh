#!/bin/bash
# ConoHa VPS デプロイスクリプト

set -e  # エラーで停止

echo "========================================="
echo "My Dungeon - ConoHa VPS デプロイ開始"
echo "========================================="

# 色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Git pull（最新コードを取得）
echo -e "${YELLOW}[1/5] 最新コードを取得中...${NC}"
git pull origin main || echo "警告: git pull失敗（初回デプロイの場合は無視）"

# 2. 環境変数チェック
echo -e "${YELLOW}[2/5] 環境変数をチェック中...${NC}"
if [ ! -f "./backend/.env" ]; then
    echo -e "${RED}エラー: backend/.env ファイルが見つかりません${NC}"
    echo "backend/.env.example をコピーして .env を作成してください"
    exit 1
fi

# 3. Docker イメージのビルド
echo -e "${YELLOW}[3/5] Dockerイメージをビルド中...${NC}"
docker-compose build --no-cache

# 4. 古いコンテナを停止・削除
echo -e "${YELLOW}[4/5] 古いコンテナを停止中...${NC}"
docker-compose down

# 5. 新しいコンテナを起動
echo -e "${YELLOW}[5/5] 新しいコンテナを起動中...${NC}"
docker-compose up -d

# 起動確認
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}デプロイ完了！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "コンテナ状態:"
docker-compose ps
echo ""
echo "ログを確認:"
echo "  docker-compose logs -f"
echo ""
echo "アプリケーションにアクセス:"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
