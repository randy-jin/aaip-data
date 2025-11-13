#!/bin/bash
# AAIP Data Tracker - 快速更新脚本
# 用途：从 git 拉取最新代码并重新部署

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

DEPLOY_PATH="/home/$USER/deploy/aaip-data"
WEB_PATH="/var/www/aaip-test"

cd "$DEPLOY_PATH"

echo "========================================"
echo "   AAIP Data Tracker 快速更新"
echo "========================================"
echo ""

# ============================================
# 步骤 1: 拉取最新代码
# ============================================
print_step "步骤 1/5: 拉取最新代码"

git fetch origin test
git checkout test
git reset --hard origin/test

print_success "代码已更新到最新版本"

# ============================================
# 步骤 2: 更新 Backend
# ============================================
print_step "步骤 2/5: 更新 Backend"

cd backend
source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate
cd ..

sudo systemctl restart aaip-backend-test
print_success "Backend 已重启"

# ============================================
# 步骤 3: 更新 Frontend
# ============================================
print_step "步骤 3/5: 更新 Frontend"

cd frontend
npm install --prefer-offline
npm run build
sudo cp -r dist/* "$WEB_PATH/"
cd ..

print_success "Frontend 已更新"

# ============================================
# 步骤 4: 更新 Scraper
# ============================================
print_step "步骤 4/5: 更新 Scraper"

cd scraper
source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate
cd ..

sudo systemctl restart aaip-scraper.timer
print_success "Scraper 已重启"

# ============================================
# 步骤 5: 更新配置文件（如果有变化）
# ============================================
print_step "步骤 5/5: 检查配置文件更新"

# 检查 systemd 文件是否有更新
if ! cmp -s deployment/aaip-backend-test.service /etc/systemd/system/aaip-backend-test.service; then
    print_info "Backend service 配置已更新"
    sudo cp deployment/aaip-backend-test.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl restart aaip-backend-test
fi

if ! cmp -s deployment/aaip-scraper.service /etc/systemd/system/aaip-scraper.service; then
    print_info "Scraper service 配置已更新"
    sudo cp deployment/aaip-scraper.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl restart aaip-scraper.timer
fi

if ! cmp -s deployment/aaip-scraper.timer /etc/systemd/system/aaip-scraper.timer; then
    print_info "Scraper timer 配置已更新"
    sudo cp deployment/aaip-scraper.timer /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl restart aaip-scraper.timer
fi

# 检查 Nginx 配置
NGINX_CONF="deployment/nginx-aaip-test-fixed.conf"
if [ ! -f "$NGINX_CONF" ]; then
    NGINX_CONF="deployment/nginx-aaip-test.conf"
fi

if ! cmp -s "$NGINX_CONF" /etc/nginx/sites-available/aaip-test; then
    print_info "Nginx 配置已更新"
    sudo cp "$NGINX_CONF" /etc/nginx/sites-available/aaip-test
    sudo nginx -t && sudo systemctl reload nginx
fi

# ============================================
# 完成
# ============================================
echo ""
echo "========================================"
print_success "更新完成！"
echo "========================================"
echo ""

print_info "服务状态："
echo "  Backend:  $(sudo systemctl is-active aaip-backend-test)"
echo "  Nginx:    $(sudo systemctl is-active nginx)"
echo "  Scraper:  $(sudo systemctl is-active aaip-scraper.timer)"
echo ""

print_info "最新提交："
git log -1 --oneline
echo ""
