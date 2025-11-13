# AAIP Data Tracker 文档索引

本目录包含所有项目文档。

## 📚 文档目录

### 快速开始
- [**部署指南**](DEPLOYMENT.md) - 完整的服务器部署教程
- [**开发指南**](DEVELOPMENT.md) - 本地开发环境设置

### 运维管理
- [**CI/CD 说明**](CI_CD.md) - GitHub Actions 自动化部署
- [**故障排查**](TROUBLESHOOTING.md) - 常见问题和解决方案

### 参考资料
- [**架构说明**](ARCHITECTURE.md) - 系统架构和技术栈
- [**API 文档**](API.md) - 后端 API 接口说明

## 🚀 快速部署

如果你只想快速部署，跳过所有文档，运行：

```bash
cd /home/randy/deploy/aaip-data
./deployment/setup-scraper.sh       # 只配置数据抓取
# 或
./deployment/deploy-all.sh          # 完整部署所有服务
```

## 📝 项目说明

AAIP Data Tracker 是一个用于追踪 Alberta Advantage Immigration Program (AAIP) 处理信息的数据可视化系统。

- **数据源**: https://www.alberta.ca/aaip-processing-information
- **更新频率**: 每小时自动抓取
- **技术栈**: Python (FastAPI + BeautifulSoup) + React + PostgreSQL
