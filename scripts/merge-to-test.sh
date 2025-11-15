#!/bin/bash
# 合并 main 分支到 test 分支并触发自动部署

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  合并 main → test 并触发部署${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  当前不在 main 分支，切换到 main...${NC}"
    git checkout main
fi

# 确保 main 分支是最新的
echo -e "${BLUE}📥 拉取 main 分支最新代码...${NC}"
git pull origin main

# 显示即将合并的提交
echo ""
echo -e "${BLUE}📝 以下提交将被合并到 test 分支:${NC}"
git log origin/test..main --oneline --graph
echo ""

# 确认合并
read -p "是否继续合并到 test 分支？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
fi

# 切换到 test 分支
echo ""
echo -e "${BLUE}🔄 切换到 test 分支...${NC}"
git checkout test

# 拉取最新的 test 分支
echo -e "${BLUE}📥 拉取 test 分支最新代码...${NC}"
git pull origin test

# 合并 main 到 test
echo -e "${BLUE}🔀 合并 main 到 test...${NC}"
if git merge main --no-edit; then
    echo -e "${GREEN}✅ 合并成功${NC}"
else
    echo -e "${YELLOW}⚠️  合并有冲突，请手动解决后运行:${NC}"
    echo "   git add ."
    echo "   git commit"
    echo "   git push origin test"
    exit 1
fi

# 推送到远程
echo -e "${BLUE}📤 推送到 origin/test...${NC}"
git push origin test

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 合并完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}GitHub Actions 将自动部署到测试服务器${NC}"
echo -e "${BLUE}查看部署状态: https://github.com/$(git remote get-url origin | sed 's/.*://;s/.git$//')/actions${NC}"
echo ""

# 切换回 main 分支
git checkout main
echo -e "${GREEN}已切换回 main 分支，可以继续开发${NC}"
