#!/bin/bash
# AAIP Data Tracker - 一键部署脚本
# 用途：在服务器上自动配置所有服务（backend、frontend、scraper）

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    print_error "请不要使用 root 用户运行此脚本"
    print_info "使用普通用户（如 randy）运行，脚本会在需要时使用 sudo"
    exit 1
fi

# 配置变量
DEPLOY_PATH="/home/$USER/deploy/aaip-data"
WEB_PATH="/var/www/aaip-test"
DATABASE_NAME="aaip_data"

# 打印欢迎信息
clear
echo "========================================"
echo "   AAIP Data Tracker 一键部署脚本"
echo "========================================"
echo ""
print_info "部署路径: $DEPLOY_PATH"
print_info "Web 路径: $WEB_PATH"
print_info "数据库: $DATABASE_NAME"
echo ""

# 确认继续
read -p "是否继续部署？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "部署已取消"
    exit 0
fi

# ============================================
# 步骤 1: 检查系统依赖
# ============================================
print_step "步骤 1/8: 检查系统依赖"

if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi
print_success "Python3: $(python3 --version)"

if ! command -v node &> /dev/null; then
    print_warning "Node.js 未安装，正在安装..."
    sudo apt update
    sudo apt install -y nodejs npm
fi
print_success "Node.js: $(node --version)"

if ! command -v nginx &> /dev/null; then
    print_warning "Nginx 未安装，正在安装..."
    sudo apt update
    sudo apt install -y nginx
fi
print_success "Nginx: $(nginx -v 2>&1)"

if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL 未安装，请先安装 PostgreSQL"
    print_info "运行: sudo apt install postgresql postgresql-contrib"
    exit 1
fi
print_success "PostgreSQL: 已安装"

# ============================================
# 步骤 2: 创建虚拟环境和安装依赖
# ============================================
print_step "步骤 2/8: 设置 Python 虚拟环境"

cd "$DEPLOY_PATH"

# Backend 虚拟环境
if [ ! -d "backend/venv" ]; then
    print_info "创建 backend 虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    deactivate
    cd ..
    print_success "Backend 虚拟环境已创建"
else
    print_info "Backend 虚拟环境已存在，跳过"
fi

# Scraper 虚拟环境
if [ ! -d "scraper/venv" ]; then
    print_info "创建 scraper 虚拟环境..."
    cd scraper
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    deactivate
    cd ..
    print_success "Scraper 虚拟环境已创建"
else
    print_info "Scraper 虚拟环境已存在，跳过"
fi

# ============================================
# 步骤 3: 配置数据库
# ============================================
print_step "步骤 3/8: 配置数据库"

if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DATABASE_NAME"; then
    print_info "数据库 $DATABASE_NAME 已存在"
else
    print_info "创建数据库 $DATABASE_NAME..."
    sudo -u postgres createdb "$DATABASE_NAME"
    print_success "数据库已创建"
fi

# 初始化数据库表结构
print_info "初始化数据库表结构..."
cd backend
source venv/bin/activate
python3 << 'PYEOF'
try:
    from database_init import init_database
    init_database()
    print("✅ 数据库初始化成功")
except Exception as e:
    print(f"⚠️  数据库可能已初始化: {e}")
PYEOF
deactivate
cd ..

# ============================================
# 步骤 4: 安装 Backend Service
# ============================================
print_step "步骤 4/8: 配置 Backend Service"

sudo cp deployment/aaip-backend-test.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/aaip-backend-test.service
sudo systemctl daemon-reload
sudo systemctl enable aaip-backend-test
sudo systemctl restart aaip-backend-test

sleep 2
if sudo systemctl is-active --quiet aaip-backend-test; then
    print_success "Backend service 已启动"
else
    print_warning "Backend service 启动失败，请检查日志"
    print_info "运行: sudo journalctl -u aaip-backend-test -n 50"
fi

# ============================================
# 步骤 5: 配置 Nginx
# ============================================
print_step "步骤 5/8: 配置 Nginx"

# 创建 web 目录
if [ ! -d "$WEB_PATH" ]; then
    sudo mkdir -p "$WEB_PATH"
    sudo chown $USER:$USER "$WEB_PATH"
    print_success "Web 目录已创建: $WEB_PATH"
fi

# 安装 Nginx 配置
if [ -f "/etc/nginx/sites-enabled/aaip-data.conf" ]; then
    print_info "Nginx 配置已存在，跳过"
else
    if [ -f "deployment/nginx-aaip-test-fixed.conf" ]; then
        sudo cp deployment/nginx-aaip-test-fixed.conf /etc/nginx/sites-available/aaip-test
    else
        sudo cp deployment/nginx-aaip-test.conf /etc/nginx/sites-available/aaip-test
    fi
    sudo ln -sf /etc/nginx/sites-available/aaip-test /etc/nginx/sites-enabled/aaip-test
    print_success "Nginx 配置已安装"
fi

# 测试并重启 Nginx
if sudo nginx -t 2>&1 | grep -q "successful"; then
    sudo systemctl restart nginx
    print_success "Nginx 配置测试通过并已重启"
else
    print_error "Nginx 配置测试失败"
    sudo nginx -t
    exit 1
fi

# ============================================
# 步骤 6: 构建和部署 Frontend
# ============================================
print_step "步骤 6/8: 构建和部署 Frontend"

cd frontend
print_info "安装 frontend 依赖..."
npm install --prefer-offline

print_info "构建 frontend..."
npm run build

print_info "部署 frontend 到 $WEB_PATH..."
sudo cp -r dist/* "$WEB_PATH/"

cd ..
print_success "Frontend 已部署"

# ============================================
# 步骤 7: 配置 Scraper Timer
# ============================================
print_step "步骤 7/8: 配置 Scraper 定时任务"

sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo cp deployment/aaip-scraper.timer /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/aaip-scraper.*
sudo systemctl daemon-reload
sudo systemctl enable aaip-scraper.timer
sudo systemctl start aaip-scraper.timer

# 手动运行一次测试
print_info "测试运行 scraper..."
sudo systemctl start aaip-scraper.service
sleep 3

if sudo journalctl -u aaip-scraper.service -n 20 | grep -q "Scraping completed"; then
    print_success "Scraper 测试成功"
else
    print_warning "Scraper 可能有问题，请检查日志"
    print_info "运行: sudo journalctl -u aaip-scraper.service -n 50"
fi

# ============================================
# 步骤 8: 配置 Sudoers
# ============================================
print_step "步骤 8/8: 配置 Sudoers 权限"

if [ -f "/etc/sudoers.d/aaip-deploy" ]; then
    print_info "Sudoers 配置已存在，跳过"
else
    sudo cp deployment/aaip-deploy-sudoers /etc/sudoers.d/aaip-deploy
    sudo chmod 440 /etc/sudoers.d/aaip-deploy

    if sudo visudo -c -f /etc/sudoers.d/aaip-deploy; then
        print_success "Sudoers 配置已安装"
    else
        print_error "Sudoers 配置语法错误"
        sudo rm /etc/sudoers.d/aaip-deploy
        exit 1
    fi
fi

# ============================================
# 部署完成总结
# ============================================
echo ""
echo "========================================"
print_success "部署完成！"
echo "========================================"
echo ""

print_info "服务状态："
echo "  Backend:  $(sudo systemctl is-active aaip-backend-test)"
echo "  Nginx:    $(sudo systemctl is-active nginx)"
echo "  Scraper:  $(sudo systemctl is-active aaip-scraper.timer)"
echo ""

print_info "访问地址："
echo "  Frontend: https://aaip.randy.it.com"
echo "  Backend:  http://localhost:8000/api/stats"
echo ""

print_info "有用的命令："
echo "  查看 backend 日志:  sudo journalctl -u aaip-backend-test -f"
echo "  查看 scraper 日志:  sudo journalctl -u aaip-scraper.service -f"
echo "  查看 nginx 日志:    sudo tail -f /var/log/nginx/aaip-test-error.log"
echo "  重启 backend:       sudo systemctl restart aaip-backend-test"
echo "  查看定时任务:       systemctl list-timers | grep aaip"
echo ""

print_warning "下一步："
echo "  1. 确保 Cloudflare Tunnel 已配置 aaip.randy.it.com"
echo "  2. 在浏览器访问 https://aaip.randy.it.com"
echo "  3. 检查数据是否正常显示"
echo ""
