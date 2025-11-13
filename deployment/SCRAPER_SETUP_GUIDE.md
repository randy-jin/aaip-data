# AAIP Scraper 自动化抓取配置指南

本指南帮助你在服务器上配置每小时自动抓取 AAIP 数据。

## 架构

```
服务器 Systemd Timer (每小时触发)
    ↓
AAIP Scraper (Python脚本)
    ↓
访问 alberta.ca/aaip-processing-information
    ↓
解析数据并存储到 PostgreSQL
```

## 前置条件

- ✅ PostgreSQL 数据库已安装并运行
- ✅ 数据库已初始化（表结构已创建）
- ✅ Scraper 代码已部署到 `/home/randy/deploy/aaip-data/scraper`
- ✅ Python 虚拟环境已创建并安装依赖

## 步骤 1：创建 Scraper 虚拟环境

```bash
cd /home/randy/deploy/aaip-data/scraper

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试 scraper
python3 scraper_enhanced.py

# 退出虚拟环境
deactivate
```

## 步骤 2：配置数据库连接

编辑 scraper service 文件中的数据库 URL（如果需要）：

```bash
cd /home/randy/deploy/aaip-data

# 查看当前配置
cat deployment/aaip-scraper.service

# 如果需要修改数据库连接，编辑文件
nano deployment/aaip-scraper.service
```

修改这一行：
```ini
Environment="DATABASE_URL=postgresql://username:password@localhost/aaip_data"
```

或者创建环境变量文件（更安全）：

```bash
# 创建环境变量文件
sudo nano /etc/default/aaip-scraper
```

添加内容：
```bash
DATABASE_URL=postgresql://aaip_user:your_password@localhost/aaip_data
```

然后修改 service 文件使用它：
```ini
EnvironmentFile=/etc/default/aaip-scraper
```

## 步骤 3：安装 Systemd Service 和 Timer

```bash
cd /home/randy/deploy/aaip-data

# 复制 service 和 timer 文件
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo cp deployment/aaip-scraper.timer /etc/systemd/system/

# 设置权限
sudo chmod 644 /etc/systemd/system/aaip-scraper.service
sudo chmod 644 /etc/systemd/system/aaip-scraper.timer

# 重新加载 systemd
sudo systemctl daemon-reload
```

## 步骤 4：启用并启动 Timer

```bash
# 启用 timer（开机自启动）
sudo systemctl enable aaip-scraper.timer

# 启动 timer
sudo systemctl start aaip-scraper.timer

# 查看 timer 状态
sudo systemctl status aaip-scraper.timer

# 查看所有 timers
systemctl list-timers --all | grep aaip
```

## 步骤 5：测试 Scraper

手动触发一次抓取以验证配置正确：

```bash
# 手动运行 scraper service
sudo systemctl start aaip-scraper.service

# 查看运行状态
sudo systemctl status aaip-scraper.service

# 查看日志
sudo journalctl -u aaip-scraper.service -n 50
```

如果成功，你应该看到：
```
✓ Successfully scraped X streams
✓ Data saved to database (X streams)
```

## 步骤 6：监控和管理

### 查看 Timer 状态

```bash
# 查看 timer 是否激活
sudo systemctl status aaip-scraper.timer

# 查看下次运行时间
systemctl list-timers | grep aaip
```

### 查看 Scraper 日志

```bash
# 实时查看日志
sudo journalctl -u aaip-scraper.service -f

# 查看最近 100 条日志
sudo journalctl -u aaip-scraper.service -n 100

# 查看今天的日志
sudo journalctl -u aaip-scraper.service --since today

# 查看最近 1 小时的日志
sudo journalctl -u aaip-scraper.service --since "1 hour ago"
```

### 手动触发抓取

```bash
# 立即运行一次（不等待定时器）
sudo systemctl start aaip-scraper.service
```

### 停止自动抓取

```bash
# 停止 timer（但不禁用）
sudo systemctl stop aaip-scraper.timer

# 禁用 timer（开机不启动）
sudo systemctl disable aaip-scraper.timer
```

### 重新启动自动抓取

```bash
# 重新启动 timer
sudo systemctl start aaip-scraper.timer

# 重新启用 timer
sudo systemctl enable aaip-scraper.timer
```

## 验证数据是否正确存储

```bash
# 连接数据库查看数据
sudo -u postgres psql aaip_data

# 在 psql 中执行：
SELECT COUNT(*) FROM aaip_summary;
SELECT COUNT(*) FROM stream_data;
SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;

# 查看最新数据
SELECT * FROM aaip_summary ORDER BY timestamp DESC LIMIT 1;
```

## 调整抓取频率

如果想修改抓取频率，编辑 timer 文件：

```bash
sudo nano /etc/systemd/system/aaip-scraper.timer
```

常见的时间配置：

```ini
# 每小时
OnCalendar=hourly

# 每 30 分钟
OnCalendar=*:0/30

# 每 2 小时
OnCalendar=0/2:00

# 每天 8:00
OnCalendar=08:00

# 工作日 9:00-17:00，每小时
OnCalendar=Mon-Fri *-*-* 09..17:00:00
```

修改后重新加载：
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer
```

## 故障排查

### Scraper 运行失败

```bash
# 查看详细错误
sudo journalctl -u aaip-scraper.service -n 100 --no-pager

# 常见问题：
# 1. 数据库连接失败
#    检查 DATABASE_URL 配置
#    检查 PostgreSQL 是否运行：sudo systemctl status postgresql

# 2. 虚拟环境未找到
#    检查路径：ls -la /home/randy/deploy/aaip-data/scraper/venv
#    重新创建虚拟环境

# 3. 权限问题
#    确保 randy 用户有权限访问目录和数据库
```

### Timer 没有触发

```bash
# 检查 timer 是否激活
systemctl is-active aaip-scraper.timer

# 检查 timer 是否启用
systemctl is-enabled aaip-scraper.timer

# 查看 timer 日志
sudo journalctl -u aaip-scraper.timer -n 50
```

### 数据库表不存在

需要先初始化数据库结构。运行：

```bash
cd /home/randy/deploy/aaip-data/backend
source venv/bin/activate
python3 -c "from database_init import init_database; init_database()"
deactivate
```

## 性能监控

### 查看抓取历史

```bash
# 查看最近 20 次抓取记录
sudo journalctl -u aaip-scraper.service --since "24 hours ago" | grep "Scraping completed"

# 统计成功次数
sudo journalctl -u aaip-scraper.service --since "7 days ago" | grep -c "success"
```

### 数据库统计

```sql
-- 连接数据库
sudo -u postgres psql aaip_data

-- 查看数据增长
SELECT
    DATE(timestamp) as date,
    COUNT(*) as records,
    COUNT(DISTINCT stream_name) as streams
FROM stream_data
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 7;

-- 查看抓取日志统计
SELECT
    status,
    COUNT(*) as count,
    MAX(timestamp) as last_occurrence
FROM scrape_log
GROUP BY status;
```

## 安全建议

1. **使用专用数据库用户**：不要使用 postgres 超级用户
2. **限制文件权限**：
   ```bash
   chmod 600 /etc/default/aaip-scraper  # 如果使用环境变量文件
   ```
3. **定期备份数据库**：
   ```bash
   pg_dump aaip_data > aaip_data_backup_$(date +%Y%m%d).sql
   ```

## 卸载

如果需要移除自动抓取：

```bash
# 停止并禁用 timer
sudo systemctl stop aaip-scraper.timer
sudo systemctl disable aaip-scraper.timer

# 删除 service 和 timer 文件
sudo rm /etc/systemd/system/aaip-scraper.service
sudo rm /etc/systemd/system/aaip-scraper.timer

# 重新加载 systemd
sudo systemctl daemon-reload
```

## 有用的命令总结

```bash
# 查看状态
sudo systemctl status aaip-scraper.timer
sudo systemctl status aaip-scraper.service

# 查看日志
sudo journalctl -u aaip-scraper.service -f

# 手动运行
sudo systemctl start aaip-scraper.service

# 重启 timer
sudo systemctl restart aaip-scraper.timer

# 查看下次运行时间
systemctl list-timers | grep aaip

# 查看最近的抓取结果
sudo journalctl -u aaip-scraper.service --since "1 hour ago"
```

## 参考

- [Systemd Timers Documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
