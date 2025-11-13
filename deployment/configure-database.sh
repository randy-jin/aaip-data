#!/bin/bash
# 配置数据库连接和初始化

set -e

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

clear
echo "========================================"
echo "   AAIP 数据库配置"
echo "========================================"
echo ""

# ============================================
# 步骤 1: 检查 PostgreSQL
# ============================================
print_step "步骤 1/5: 检查 PostgreSQL"

if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL 未安装"
    print_info "请运行: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

if ! sudo systemctl is-active --quiet postgresql; then
    print_info "启动 PostgreSQL..."
    sudo systemctl start postgresql
fi

print_success "PostgreSQL 正在运行"

# ============================================
# 步骤 2: 创建数据库
# ============================================
print_step "步骤 2/5: 创建数据库"

DB_NAME="aaip_data_trend_dev_db"

if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    print_info "数据库 $DB_NAME 已存在"
else
    print_info "创建数据库 $DB_NAME..."
    sudo -u postgres createdb "$DB_NAME"
    print_success "数据库已创建"
fi

# ============================================
# 步骤 3: 配置数据库用户（可选）
# ============================================
print_step "步骤 3/5: 配置数据库连接"

echo ""
print_info "选择数据库连接方式："
echo "  1. 使用 peer 认证（推荐，无需密码）"
echo "  2. 使用密码认证"
echo ""
read -p "请选择 (1/2): " -n 1 -r
echo ""

if [[ $REPLY == "2" ]]; then
    # 使用密码认证
    read -p "输入数据库用户名 [aaip_user]: " DB_USER
    DB_USER=${DB_USER:-aaip_user}

    read -sp "输入数据库密码: " DB_PASSWORD
    echo ""

    # 创建用户
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

    DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME"

    print_success "数据库用户已配置"
else
    # 使用 peer 认证（当前系统用户）
    DATABASE_URL="postgresql://localhost/$DB_NAME"

    # 确保当前用户有数据库访问权限
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $USER;" 2>/dev/null || true

    print_success "使用 peer 认证（无需密码）"
fi

# ============================================
# 步骤 4: 更新 systemd 服务配置
# ============================================
print_step "步骤 4/5: 更新服务配置"

DEPLOY_PATH="/home/$USER/deploy/aaip-data"

# 更新 backend service
sudo sed -i "s|Environment=\"DATABASE_URL=.*\"|Environment=\"DATABASE_URL=$DATABASE_URL\"|" /etc/systemd/system/aaip-backend-test.service 2>/dev/null || true

# 更新 scraper service
sudo sed -i "s|Environment=\"DATABASE_URL=.*\"|Environment=\"DATABASE_URL=$DATABASE_URL\"|" /etc/systemd/system/aaip-scraper.service 2>/dev/null || true

sudo systemctl daemon-reload

print_success "服务配置已更新"

# ============================================
# 步骤 5: 初始化数据库表结构
# ============================================
print_step "步骤 5/5: 初始化数据库表结构"

cd "$DEPLOY_PATH/backend"
source venv/bin/activate

export DATABASE_URL="$DATABASE_URL"

python3 << PYEOF
try:
    from database_init import init_database
    init_database()
    print("✅ 数据库表结构初始化成功")
except Exception as e:
    print(f"⚠️  初始化失败或表已存在: {e}")
PYEOF

deactivate

# ============================================
# 测试连接
# ============================================
echo ""
print_info "测试数据库连接..."

cd "$DEPLOY_PATH/scraper"
source venv/bin/activate

export DATABASE_URL="$DATABASE_URL"

if python3 -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); conn.close(); print('✅ 连接成功')" 2>/dev/null; then
    print_success "数据库连接测试成功"
else
    print_error "数据库连接测试失败"
    deactivate
    exit 1
fi

deactivate

# ============================================
# 完成
# ============================================
echo ""
echo "========================================"
print_success "数据库配置完成！"
echo "========================================"
echo ""

print_info "数据库信息："
echo "  数据库名: $DB_NAME"
echo "  连接 URL: $DATABASE_URL"
echo ""

print_info "现在可以运行："
echo "  ./deployment/setup-scraper.sh    # 配置定时抓取"
echo "  或"
echo "  ./deployment/deploy-all.sh       # 完整部署"
echo ""
