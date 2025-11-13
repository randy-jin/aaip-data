# CI/CD with Direct SSH (No Cloudflare SSH)

## Overview

The CI/CD pipeline now uses **direct SSH** instead of Cloudflare Tunnel SSH because:
- Your Cloudflare Tunnel only has HTTP ingress rules (not SSH)
- Direct SSH is simpler and more reliable for deployment
- Your Cloudflare Tunnel is still used for web traffic (glaze.randy.it.com)

## Architecture

```
GitHub Actions Runner
    ↓ (Direct SSH)
Your Workstation (100.77.247.113 or public IP)
    ↓ (Cloudflare Tunnel - HTTP only)
Internet Users → glaze.randy.it.com
```

## Required GitHub Secrets

### SSH Access
- `SSH_PRIVATE_KEY`: Your SSH private key for passwordless login
- `SSH_USER`: `jinzhiqiang`
- `SSH_HOST`: Your workstation's public IP or hostname

### Deployment Paths
- `TEST_DEPLOY_PATH`: `/Users/jinzhiqiang/workspaces/doit/aaip-data`

### Service URLs (for logging only)
- `TEST_BACKEND_URL`: `http://localhost:8000`
- `TEST_FRONTEND_URL`: `http://localhost:3002`

### Database
- `TEST_DATABASE_URL`: `postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db`

## Setup Steps

### 1. Generate SSH Key on Your Workstation

```bash
# On your workstation
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

### 2. Add Public Key to Authorized Keys

```bash
# On your workstation
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Add Private Key to GitHub Secrets

```bash
# Copy the private key
cat ~/.ssh/github_actions

# Go to GitHub: Settings → Secrets → Actions → New repository secret
# Name: SSH_PRIVATE_KEY
# Value: Paste the entire private key (including -----BEGIN/END-----)
```

### 4. Ensure SSH Port is Accessible

Your workstation needs to be accessible from GitHub's IP ranges:

```bash
# Check if SSH is running
sudo systemctl status ssh

# If you're behind a router, forward port 22 to your workstation
# Or use a different port and add it to SSH_HOST like: hostname:2222
```

### 5. Set All GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/aaip-data/settings/secrets/actions`

Required secrets:
```yaml
SSH_PRIVATE_KEY: (your private key from step 3)
SSH_USER: jinzhiqiang
SSH_HOST: YOUR_PUBLIC_IP_OR_HOSTNAME
TEST_DEPLOY_PATH: /Users/jinzhiqiang/workspaces/doit/aaip-data
TEST_BACKEND_URL: http://localhost:8000
TEST_FRONTEND_URL: http://localhost:3002
TEST_DATABASE_URL: postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db
```

## CI/CD Workflow

### Trigger
- Push to `test` branch
- Pull request to `test` branch

### Jobs

#### 1. Test Job
Runs on GitHub's Ubuntu runner:
- ✅ Install Python & Node.js dependencies
- ✅ Test scraper module imports
- ✅ Test backend module imports
- ✅ Build frontend
- ✅ Verify build artifacts

#### 2. Deploy Job (only on push)
Connects via SSH to your workstation:
- 🔑 Setup SSH authentication
- 📥 Pull latest code from git
- 🔧 Update backend (install deps + restart service)
- 🎨 Update frontend (build + copy to /var/www/aaip-test/)
- 🔄 Update scraper dependencies
- 💚 Health checks (from within workstation)
- 📊 Deployment summary

## Troubleshooting

### SSH Connection Fails

```bash
# Test SSH from your local machine
ssh -i ~/.ssh/github_actions jinzhiqiang@YOUR_HOST

# Check SSH logs on workstation
sudo tail -f /var/log/auth.log
```

### Health Checks Fail

The health checks run **on your workstation** (not from GitHub):
- Backend: `curl http://localhost:8000`
- Frontend: `curl http://localhost:3002`

Make sure both services are running:

```bash
# Check backend
sudo systemctl status aaip-backend-test
curl http://localhost:8000

# Check frontend (Vite dev server)
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/frontend
npm run dev
```

### Permission Issues

If deployment fails with permission errors:

```bash
# Ensure user can restart services without password
sudo visudo
# Add: jinzhiqiang ALL=(ALL) NOPASSWD: /bin/systemctl restart aaip-backend-test

# Ensure web directory is writable
sudo chown -R jinzhiqiang:jinzhiqiang /var/www/aaip-test/
```

## Alternative: Cloudflare Tunnel SSH

If you want to use Cloudflare Tunnel for SSH (more secure for home networks), you need to:

1. Update your `~/.cloudflared/config.yml`:

```yaml
tunnel: 39b2663b-cc31-48df-a461-9aaa5dd00137
credentials-file: /home/randy/.cloudflared/39b2663b-cc31-48df-a461-9aaa5dd00137.json

ingress:
  - hostname: glaze.randy.it.com
    service: http://localhost:80
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22  # ← Add this
  - service: http_status:404
```

2. Restart the tunnel:

```bash
sudo systemctl restart cloudflared
```

3. Use the Cloudflare SSH workflow (more complex, requires service tokens)

## Current Status

✅ **Direct SSH** - Simple, works immediately
❌ Cloudflare Tunnel SSH - Requires tunnel reconfiguration

The current setup uses direct SSH for simplicity and reliability.
