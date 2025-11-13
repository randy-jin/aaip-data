#!/bin/bash
# AAIP Scraper 一键配置脚本
# 用途：自动配置 scraper 的虚拟环境、systemd service 和 timer

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 配置变量
DEPLOY_PATH="/home/$USER/deploy/aaip-data"
SCRAPER_PATH="$DEPLOY_PATH/scraper"

clear
echo "========================================"
echo "   AAIP Scraper 一键配置"
echo "========================================"
echo ""
print_info "将配置每小时自动抓取 AAIP 数据"
print_info "Scraper 路径: $SCRAPER_PATH"
echo ""

# 确认继续
read -p "是否继续？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "已取消"
    exit 0
fi

# ============================================
# 步骤 1: 创建虚拟环境
# ============================================
print_step "步骤 1/5: 创建 Python 虚拟环境"

cd "$SCRAPER_PATH"

if [ -d "venv" ]; then
    print_info "虚拟环境已存在，跳过创建"
else
    print_info "创建虚拟环境..."
    python3 -m venv venv
    print_success "虚拟环境已创建"
fi

# ============================================
# 步骤 2: 安装依赖
# ============================================
print_step "步骤 2/5: 安装 Python 依赖"

source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate

print_success "依赖安装完成"

# ============================================
# 步骤 3: 检查数据库连接
# ============================================
print_step "步骤 3/5: 检查数据库连接"

source venv/bin/activate

# 尝试连接数据库
if python3 -c "import psycopg2; import os; conn = psycopg2.connect(os.getenv('DATABASE_URL', 'dbname=aaip_data_trend_dev_db')); conn.close(); print('✅ 数据库连接成功')" 2>/dev/null; then
    print_success "数据库连接正常"
else
    print_error "数据库连接失败"
    echo ""
    print_info "尝试自动配置数据库权限..."

    # 授权当前用户访问数据库
    if sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aaip_data_trend_dev_db TO $USER;" 2>/dev/null; then
        print_success "数据库权限已配置"

        # 再次测试连接
        if python3 -c "import psycopg2; import os; conn = psycopg2.connect(os.getenv('DATABASE_URL', 'dbname=aaip_data_trend_dev_db')); conn.close(); print('✅ 数据库连接成功')" 2>/dev/null; then
            print_success "数据库连接正常"
        else
            print_error "仍然无法连接数据库"
            echo ""
            print_info "需要手动配置 PostgreSQL 认证："
            echo "  1. 编辑配置文件: sudo nano /etc/postgresql/*/main/pg_hba.conf"
            echo "  2. 找到这一行: local   all   all   peer"
            echo "  3. 改为: local   all   all   trust"
            echo "  4. 重启: sudo systemctl restart postgresql"
            echo ""
            deactivate
            exit 1
        fi
    else
        print_error "无法自动配置权限"
        echo ""
        print_info "请手动执行："
        echo "  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE aaip_data_trend_dev_db TO $USER;\""
        echo ""
        deactivate
        exit 1
    fi
fi

# ============================================
# 步骤 4: 测试运行
# ============================================
print_step "步骤 4/6: 测试 Scraper"

print_info "运行一次测试..."
if python3 scraper_enhanced.py; then
    print_success "Scraper 测试成功"
else
    print_error "Scraper 测试失败"
    deactivate
    exit 1
fi
deactivate

# ============================================
# 步骤 5: 安装 Systemd Service 和 Timer
# ============================================
print_step "步骤 5/6: 安装 Systemd Service 和 Timer"

cd "$DEPLOY_PATH"

print_info "安装 aaip-scraper.service..."
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/aaip-scraper.service

print_info "安装 aaip-scraper.timer..."
sudo cp deployment/aaip-scraper.timer /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/aaip-scraper.timer

print_info "重新加载 systemd..."
sudo systemctl daemon-reload

print_success "Service 和 Timer 已安装"

# ============================================
# 步骤 6: 启用并启动 Timer
# ============================================
print_step "步骤 6/6: 启用并启动定时任务"

print_info "启用 timer（开机自启动）..."
sudo systemctl enable aaip-scraper.timer

print_info "启动 timer..."
sudo systemctl start aaip-scraper.timer

sleep 2

if sudo systemctl is-active --quiet aaip-scraper.timer; then
    print_success "Timer 已启动"
else
    print_error "Timer 启动失败"
    exit 1
fi

# ============================================
# 完成
# ============================================
echo ""
echo "========================================"
print_success "配置完成！"
echo "========================================"
echo ""

print_info "状态检查："
sudo systemctl status aaip-scraper.timer --no-pager -l

echo ""
print_info "下次运行时间："
systemctl list-timers | grep aaip

echo ""
print_info "有用的命令："
echo "  查看 timer 状态:     sudo systemctl status aaip-scraper.timer"
echo "  查看 scraper 日志:   sudo journalctl -u aaip-scraper.service -f"
echo "  手动触发抓取:        sudo systemctl start aaip-scraper.service"
echo "  停止自动抓取:        sudo systemctl stop aaip-scraper.timer"
echo "  重新启动:            sudo systemctl restart aaip-scraper.timer"
echo ""

print_success "Scraper 现在会每小时自动运行一次！"
