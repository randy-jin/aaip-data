# AAIP Data Tracker

实时追踪和可视化 Alberta Advantage Immigration Program (AAIP) 的处理信息。

## 🚀 快速部署

### 方式一：完整部署（推荐）

在服务器上运行一键部署脚本：

```bash
cd /home/randy/deploy/aaip-data
./deployment/deploy-all.sh
```

自动完成：Backend + Frontend + Scraper + Nginx + Database 配置

### 方式二：只配置数据抓取

如果只需要定时抓取数据：

```bash
cd /home/randy/deploy/aaip-data
./deployment/setup-scraper.sh
```

## 📊 功能特性

- ✅ **自动数据抓取** - 每小时自动从 alberta.ca 抓取最新数据
- ✅ **多流支持** - 追踪所有 AAIP 流和子流程
- ✅ **数据可视化** - 交互式图表展示历史趋势
- ✅ **实时更新** - 数据变化时自动更新
- ✅ **历史追踪** - 保存所有历史数据用于分析

## 🏗️ 技术架构

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │ ───▶ │   FastAPI    │ ───▶ │ PostgreSQL  │
│  Frontend   │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                              ▲
                              │
                     ┌────────┴────────┐
                     │  BeautifulSoup  │
                     │     Scraper     │
                     └─────────────────┘
                              ▲
                              │
                     [alberta.ca/aaip]
```

## 📁 项目结构

```
aaip-data/
├── backend/           # FastAPI 后端服务
├── frontend/          # React 前端应用
├── scraper/           # 数据抓取脚本
├── deployment/        # 部署脚本和配置
│   ├── deploy-all.sh          # 完整部署脚本
│   ├── setup-scraper.sh       # Scraper 配置脚本
│   ├── update.sh              # 快速更新脚本
│   ├── aaip-backend-test.service
│   ├── aaip-scraper.service
│   ├── aaip-scraper.timer
│   ├── nginx-aaip-test.conf
│   └── aaip-deploy-sudoers
└── docs/              # 完整文档
```

## 📚 文档

详细文档请查看 [`docs/`](docs/) 目录：

- [部署指南](docs/DEPLOYMENT.md) - 完整部署教程
- [前端配置](docs/FRONTEND_SETUP.md) - Nginx 和访问配置
- [Scraper 配置](docs/SCRAPER_SETUP.md) - 数据抓取详细说明
- [故障排查](docs/NGINX_TROUBLESHOOTING.md) - 常见问题解决
- [开发指南](docs/CLAUDE.md) - 开发环境和 API

## 🔄 日常更新

当有新代码时，运行更新脚本：

```bash
cd /home/randy/deploy/aaip-data
./deployment/update.sh
```

自动完成：拉取代码 + 更新依赖 + 重启服务

## 🌐 访问地址

部署完成后访问：

- **前端**: https://aaip.randy.it.com
- **后端 API**: https://aaip.randy.it.com/api/stats

## 🛠️ 常用命令

```bash
# 查看服务状态
sudo systemctl status aaip-backend-test
sudo systemctl status aaip-scraper.timer

# 查看日志
sudo journalctl -u aaip-backend-test -f
sudo journalctl -u aaip-scraper.service -f

# 手动触发抓取
sudo systemctl start aaip-scraper.service

# 重启服务
sudo systemctl restart aaip-backend-test
```

## 📊 数据库

```bash
# 连接数据库
sudo -u postgres psql aaip_data

# 查看数据
SELECT * FROM aaip_summary ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM stream_data ORDER BY timestamp DESC LIMIT 10;
```

## 🤝 开发流程

### 分支策略

- **main**: 开发分支，日常开发在此进行
- **test**: 测试/预发布分支，验证后手动合并 main → test

### CI/CD

- **Test Branch**: 推送到 `test` 分支自动部署到测试服务器
- **Scraper**: GitHub Actions 只验证代码，实际抓取在服务器本地运行

### 合并流程

```bash
# 1. 在 main 分支开发
git checkout main
git add .
git commit -m "your changes"
git push origin main

# 2. 验证没问题后，合并到 test 分支
git checkout test
git merge main
git push origin test

# 3. 自动触发部署到测试服务器
```

## 📝 License

MIT

## 👨‍💻 开发

本地开发请参考 [开发指南](docs/CLAUDE.md)
