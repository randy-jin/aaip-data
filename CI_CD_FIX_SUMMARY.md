# CI/CD 部署问题修复总结

## 🎯 问题诊断

### 原始问题
GitHub Actions workflow 在部署阶段失败，错误信息：
- `websocket: bad handshake`
- `permission denied` on port 22

### 根本原因
1. ❌ 使用了 `cloudflared access ssh` 命令，但实际上服务器配置的是纯 Tunnel SSH（无 Cloudflare Access）
2. ❌ 尝试在非特权端口（22）上监听，导致权限错误
3. ❌ 错误地使用 Service Token JSON 文件作为 `--identity-file`
4. ❌ 缺少必需的 GitHub Secret: `TEST_DEPLOY_PATH`

---

## ✅ 解决方案

### 修改内容

#### 1. 正确的连接方式
**之前（错误）**：
```bash
cloudflared access ssh --hostname ssh.randy.it.com --identity-file token.json
```

**现在（正确）**：
```bash
# 启动 TCP 代理到本地高端口
cloudflared access tcp --hostname ssh.randy.it.com --url tcp://localhost:2222 &

# 通过本地端口 SSH 连接
ssh -p 2222 randy@localhost
```

#### 2. 移除不需要的组件
- ❌ 删除 Service Token JSON 文件创建
- ❌ 删除 `CF_SERVICE_CLIENT_ID` 和 `CF_SERVICE_CLIENT_SECRET` 环境变量（不再需要）
- ✅ 保留 `CF_SSH_HOSTNAME` (ssh.randy.it.com)

#### 3. 添加 SSH 密钥认证
添加了新的步骤来配置 GitHub Actions 的 SSH 密钥，实现无密码登录。

---

## 📋 完整部署清单

### Step 1: 在服务器上配置 SSH 密钥

```bash
# 生成密钥对（在服务器上执行）
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key -N ""

# 添加公钥到 authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 设置正确的权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_key

# 查看私钥（要添加到 GitHub）
cat ~/.ssh/github_actions_key
```

### Step 2: 添加 GitHub Secrets

在 GitHub 仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加/更新：

| Secret Name | Value | 状态 |
|------------|-------|------|
| `SSH_USER` | `randy` | ✅ 已存在 |
| `CF_SSH_HOSTNAME` | `ssh.randy.it.com` | ✅ 已存在 |
| `TEST_DEPLOY_PATH` | `/home/randy/aaip-data` | ⚠️ **需要添加** |
| `SSH_PRIVATE_KEY` | `[完整私钥内容]` | ⚠️ **需要添加** |
| `TEST_BACKEND_URL` | `https://test-api.randy.it.com` | ✅ 已存在 |
| `TEST_FRONTEND_URL` | `https://test-frontend.randy.it.com` | ✅ 已存在 |

**不再需要的 Secrets**（可以保留但不会被使用）：
- ~~`CF_SERVICE_CLIENT_ID`~~
- ~~`CF_SERVICE_CLIENT_SECRET`~~
- ~~`CF_TUNNEL_ID`~~

### Step 3: 本地验证测试

在提交之前，先在本地测试连接：

```bash
# 测试 1: 启动 TCP 代理
cloudflared access tcp --hostname ssh.randy.it.com --url tcp://localhost:2222 &
sleep 2

# 测试 2: SSH 连接
ssh -p 2222 -i ~/.ssh/github_actions_key randy@localhost

# 测试 3: 执行远程命令
ssh -p 2222 -i ~/.ssh/github_actions_key randy@localhost "cd /home/randy/aaip-data && git status"

# 清理
pkill cloudflared
```

### Step 4: 提交并测试

```bash
# 查看修改
git status
git diff .github/workflows/test-deploy.yml

# 提交修改
git add .github/workflows/test-deploy.yml
git commit -m "Fix CI/CD deployment via Cloudflare Tunnel

- Use cloudflared TCP proxy instead of access ssh
- Add SSH key authentication
- Remove Service Token usage (not needed for pure tunnel)
- Fix port permission issues by using high port (2222)
- Add TEST_DEPLOY_PATH secret requirement

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送到 test 分支触发 CI/CD
git push origin test
```

---

## 🔍 工作原理

### 修改后的部署流程

```
GitHub Actions Runner
    ↓
1. Install cloudflared CLI
    ↓
2. Setup SSH key from secrets
    ↓
3. Start TCP proxy: cloudflared → ssh.randy.it.com
   (在 GitHub Actions 的 localhost:2222 监听)
    ↓
4. SSH 连接到 localhost:2222
    ↓ (通过 Cloudflare Tunnel 转发)
    ↓
家庭服务器 ssh.randy.it.com:22
    ↓
5. 执行部署命令
    - git pull
    - 安装依赖
    - 重启服务
```

---

## 🧪 验证部署成功

部署完成后，检查这些端点：

```bash
# 检查后端 API
curl https://test-api.randy.it.com/api/stats

# 检查前端
curl https://test-frontend.randy.it.com

# 在服务器上检查服务状态
ssh randy@ssh.randy.it.com
sudo systemctl status aaip-backend-test
```

---

## 🐛 常见问题排查

### 问题 1: SSH 连接超时
```bash
# 检查 tunnel 状态
sudo systemctl status cloudflared

# 查看 tunnel 日志
sudo journalctl -u cloudflared -n 50
```

### 问题 2: SSH 认证失败
```bash
# 检查 SSH 密钥权限
ls -la ~/.ssh/
# 应该看到：
# -rw------- github_actions_key
# -rw------- authorized_keys

# 测试密钥
ssh -p 2222 -i ~/.ssh/github_actions_key -v randy@localhost
```

### 问题 3: 部署命令执行失败
```bash
# 检查部署路径是否正确
cd /home/randy/aaip-data  # 使用你设置的 TEST_DEPLOY_PATH

# 检查 systemd 服务
sudo systemctl status aaip-backend-test

# 检查 web 目录权限
ls -la /var/www/aaip-test/
```

---

## 📚 参考文档

- [Cloudflare Tunnel 文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/public-key-authentication)

---

## ✨ 关键改进

1. ✅ 简化了部署流程（移除了不必要的 Access 认证）
2. ✅ 解决了端口权限问题（使用高端口 2222）
3. ✅ 添加了正确的 SSH 密钥认证
4. ✅ 修复了 cloudflared 命令使用方式
5. ✅ 添加了进程清理（防止资源泄漏）

---

**生成时间**: 2025-11-13
**Cloudflare Tunnel ID**: `39b2663b-cc31-48df-a461-9aaa5dd00137`
**Tunnel Name**: `randy_workstation_at_home`
