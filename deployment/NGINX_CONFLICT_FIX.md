# Nginx 配置冲突解决方案

## 问题诊断

你当前有两个 Nginx 配置文件都在监听端口 80 和域名 `glaze.randy.it.com`：

1. `/etc/nginx/sites-enabled/glaze.conf` - Glaze 服务（React 前端 + API）
2. `/etc/nginx/sites-enabled/aaip-data.conf` - AAIP 服务（错误地使用了同一个域名）

这会导致 Nginx 无法正确路由请求。

---

## 方案 1：独立域名（推荐）✅

为 AAIP 使用独立的域名，保持两个服务完全分离。

### 优点
- ✅ 清晰分离，互不干扰
- ✅ 易于管理和维护
- ✅ 可以独立设置安全策略

### 配置步骤

#### 1. 删除错误的配置文件

```bash
sudo rm /etc/nginx/sites-enabled/aaip-data.conf
sudo rm /etc/nginx/sites-available/aaip-data.conf
```

#### 2. 安装正确的配置

```bash
cd /home/randy/deploy/aaip-data

# 使用修复后的配置文件
sudo cp deployment/nginx-aaip-test-fixed.conf /etc/nginx/sites-available/aaip-test
sudo ln -s /etc/nginx/sites-available/aaip-test /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 3. 配置 Cloudflare Tunnel

编辑 `~/.cloudflared/config.yml`：

```yaml
tunnel: 39b2663b-cc31-48df-a461-9aaa5dd00137
credentials-file: /home/randy/.cloudflared/39b2663b-cc31-48df-a461-9aaa5dd00137.json

ingress:
  # Glaze 服务（保持不变）
  - hostname: glaze.randy.it.com
    service: http://localhost:80

  # SSH 访问（保持不变）
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22

  # AAIP 服务（新增独立域名）
  - hostname: aaip-test.randy.it.com
    service: http://localhost:80

  # Catch-all
  - service: http_status:404
```

重启 Cloudflare Tunnel：

```bash
sudo systemctl restart cloudflared
```

#### 4. 在 Cloudflare Dashboard 添加 DNS

访问 **Cloudflare Zero Trust** → **Access** → **Tunnels** → 你的 tunnel → **Public Hostname**

添加：
- **Subdomain**: `aaip-test`
- **Domain**: `randy.it.com`
- **Service**: `HTTP`
- **URL**: `localhost:80`

#### 5. 访问

- **Glaze**: `https://glaze.randy.it.com/`
- **AAIP**: `https://aaip-test.randy.it.com/`

---

## 方案 2：合并到同一个域名

如果你想在 `glaze.randy.it.com` 下同时访问两个服务。

### 优点
- ✅ 只使用一个域名
- ✅ 节省 Cloudflare DNS 记录

### 缺点
- ⚠️ 路径冲突风险较高
- ⚠️ 需要修改前端路由配置
- ⚠️ API 路径可能冲突

### 配置步骤

#### 1. 备份并删除现有配置

```bash
# 备份现有配置
sudo cp /etc/nginx/sites-available/glaze.conf /etc/nginx/sites-available/glaze.conf.backup

# 删除 aaip-data.conf
sudo rm /etc/nginx/sites-enabled/aaip-data.conf
sudo rm /etc/nginx/sites-available/aaip-data.conf
```

#### 2. 安装合并后的配置

```bash
cd /home/randy/deploy/aaip-data

# 使用合并配置替换 glaze.conf
sudo cp deployment/nginx-glaze-merged.conf /etc/nginx/sites-available/glaze

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 3. 访问路径

- **Glaze 前端**: `https://glaze.randy.it.com/`
- **AAIP 前端**: `https://glaze.randy.it.com/aaip/`
- **AAIP API**: `https://glaze.randy.it.com/api/`

**注意**：这种方案需要修改 AAIP 前端的路由配置（React Router 的 basename）。

---

## 推荐配置（方案 1）

我强烈推荐使用**方案 1**（独立域名），原因如下：

### 当前状态
- ✅ Glaze: `glaze.randy.it.com` → React(3000) + API(8080)
- ❌ AAIP: 使用错误的配置

### 目标状态
- ✅ Glaze: `glaze.randy.it.com` → React(3000) + API(8080)
- ✅ AAIP: `aaip-test.randy.it.com` → Static Files(/var/www/aaip-test) + API(8000)

### 执行命令（方案 1）

```bash
# 1. 清理错误配置
sudo rm /etc/nginx/sites-enabled/aaip-data.conf
sudo rm /etc/nginx/sites-available/aaip-data.conf

# 2. 安装正确配置
cd /home/randy/deploy/aaip-data
sudo cp deployment/nginx-aaip-test-fixed.conf /etc/nginx/sites-available/aaip-test
sudo ln -s /etc/nginx/sites-available/aaip-test /etc/nginx/sites-enabled/

# 3. 测试并重启
sudo nginx -t
sudo systemctl restart nginx

# 4. 更新 Cloudflare Tunnel
sudo nano ~/.cloudflared/config.yml
# 添加 aaip-test.randy.it.com 的 ingress 规则

sudo systemctl restart cloudflared

# 5. 在 Cloudflare Dashboard 添加 DNS 记录
```

---

## 验证配置

### 检查 Nginx 配置

```bash
# 列出所有启用的站点
ls -la /etc/nginx/sites-enabled/

# 应该看到：
# glaze -> /etc/nginx/sites-available/glaze
# aaip-test -> /etc/nginx/sites-available/aaip-test

# 测试配置语法
sudo nginx -t
```

### 检查端口监听

```bash
# 应该只有一个进程监听 80 端口
sudo lsof -i :80

# 检查服务状态
sudo systemctl status nginx
```

### 测试访问

```bash
# 测试 Glaze
curl -H "Host: glaze.randy.it.com" http://localhost/

# 测试 AAIP
curl -H "Host: aaip-test.randy.it.com" http://localhost/
```

---

## 故障排查

### Nginx 启动失败

```bash
# 查看详细错误
sudo nginx -t
sudo journalctl -u nginx -n 50

# 常见错误：
# 1. 端口已被占用
# 2. 配置文件语法错误
# 3. 权限问题
```

### 域名无法访问

```bash
# 检查 Cloudflare Tunnel
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -n 50

# 检查 DNS 解析
dig aaip-test.randy.it.com
```

### API 请求失败

```bash
# 检查后端服务
sudo systemctl status aaip-backend-test
curl http://localhost:8000/api/stats

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/aaip-test-error.log
```

---

## 总结

选择**方案 1**（独立域名）可以获得：
- 🎯 清晰的服务分离
- 🔒 独立的安全策略
- 🚀 更好的性能监控
- 🛠️ 更简单的维护

完成配置后，你将拥有：
- `https://glaze.randy.it.com/` - 你的 Glaze 服务
- `https://aaip-test.randy.it.com/` - AAIP 数据追踪器
