# CI/CD Pipeline Setup Guide

## Overview

This project has CI/CD configured for automatic testing and deployment to test server.

## Workflow Trigger

**When:** Code is merged/pushed to `test` branch

**What happens:**
1. ✅ Runs automated tests
2. ✅ Builds frontend
3. ✅ Deploys to test server
4. ✅ Health checks

## Required GitHub Secrets

Go to: **GitHub Repo → Settings → Secrets and variables → Actions**

Add these secrets:

### Cloudflare Tunnel Authentication
- `CF_SERVICE_CLIENT_ID` - Cloudflare Service Token Client ID
- `CF_SERVICE_CLIENT_SECRET` - Cloudflare Service Token Client Secret  
- `CF_TUNNEL_ID` - Your Cloudflare Tunnel ID
- `CF_SSH_HOSTNAME` - SSH hostname through Cloudflare (e.g., `ssh.randy.it.com`)

### Server Access
- `SSH_USER` - SSH username on your workstation (e.g., `randy` or `ubuntu`)

### Database
- `TEST_DATABASE_URL`
  ```
  postgresql://randy:password@100.77.247.113:5432/aaip_data_trend_dev_db
  ```

### Deployment Paths
- `TEST_DEPLOY_PATH` - Path on server where code is deployed
  ```
  /Users/jinzhiqiang/workspaces/doit/aaip-data
  ```

### Health Check URLs
- `TEST_BACKEND_URL` - Backend health check URL
  ```
  http://localhost:8000
  ```
- `TEST_FRONTEND_URL` - Frontend URL
  ```
  http://localhost:3002
  ```

## Cloudflare Tunnel Setup

### Prerequisites on Your Workstation:

This setup uses **Cloudflare Tunnel SSH** to securely connect GitHub Actions to your home workstation.

1. **Cloudflare Tunnel already configured:**
   - SSH accessible via: `ssh.randy.it.com`
   - Tunnel ID: Available in Cloudflare dashboard

2. **Create Service Token for GitHub Actions:**
```bash
# Login to Cloudflare
cloudflared login

# Create service token for SSH access
# Go to Cloudflare Zero Trust Dashboard → Access → Service Auth
# Create new Service Token with SSH access
# Save Client ID and Secret for GitHub Secrets
```

3. **Git repository cloned on workstation:**
```bash
cd /Users/jinzhiqiang/workspaces/doit
# Repository should already be here at: aaip-data
cd aaip-data
git checkout test
```

2. **Python environment (already done):**
```bash
# Should already be installed
python3 --version
pip3 --version
```

3. **Node.js (already done):**
```bash
# Should already be installed  
node --version
npm --version
```

4. **Backend service (systemd) - macOS alternative:**

For macOS, use LaunchAgent instead:

Create `~/Library/LaunchAgents/com.aaip.backend-test.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aaip.backend-test</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>main_enhanced:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/jinzhiqiang/workspaces/doit/aaip-data/backend</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>DATABASE_URL</key>
        <string>postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/aaip-backend-test.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/aaip-backend-test-error.log</string>
</dict>
</plist>
```

Load and start:
```bash
launchctl load ~/Library/LaunchAgents/com.aaip.backend-test.plist
launchctl start com.aaip.backend-test

# Check status
launchctl list | grep aaip
```

For Linux, use systemd (original instructions):
```ini
# /etc/systemd/system/aaip-backend-test.service
[Unit]
Description=AAIP Backend Test
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aaip-data/backend
Environment="DATABASE_URL=postgresql://randy:password@host:5432/aaip_data_test"
ExecStart=/usr/bin/python3 -m uvicorn main_enhanced:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Frontend - For macOS (dev server or nginx):**

**Option A: Use Vite dev server (for testing):**
```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/frontend
npm run dev -- --host 0.0.0.0 --port 3002
```

**Option B: Use nginx (production-like):**
```bash
# Install nginx via Homebrew
brew install nginx

# Configure nginx
sudo nano /usr/local/etc/nginx/nginx.conf
```

Add server block:
```nginx
server {
    listen 3002;
    server_name localhost;
    
    root /Users/jinzhiqiang/workspaces/doit/aaip-data/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Start nginx:
```bash
brew services start nginx
# Or manually: nginx
```

**For Linux (original instructions):**
```bash
sudo apt install nginx

# Configure nginx
sudo nano /etc/nginx/sites-available/aaip-test
```

Add:
```nginx
server {
    listen 3002;
    server_name _;
    
    root /var/www/aaip-test;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/aaip-test /etc/nginx/sites-enabled/
sudo mkdir -p /var/www/aaip-test
sudo chown ubuntu:ubuntu /var/www/aaip-test
sudo nginx -t
sudo systemctl reload nginx
```

6. **Cloudflare Tunnel Access (No SSH keys needed!):**

The beauty of Cloudflare Tunnel is that GitHub Actions doesn't need SSH keys stored!

Instead, it uses:
- Service Token authentication
- Short-lived certificates
- Automatic SSH proxy through Cloudflare

**Verify your tunnel is working:**
```bash
# From anywhere with cloudflared installed
cloudflared access ssh --hostname ssh.randy.it.com

# Should connect to your workstation
```

## Workflow Jobs

### 1. Test Job
- Checks out code
- Sets up Python and Node.js
- Installs dependencies
- Runs module import tests
- Builds frontend
- Validates build output

### 2. Deploy Job (only on push to test branch)
- SSH into test server
- Pulls latest code from test branch
- Updates dependencies
- Restarts backend service
- Builds and deploys frontend
- Runs health checks

## Usage

### Deploy to Test:

**Option 1: Direct push**
```bash
git checkout test
git merge main
git push origin test
```

**Option 2: Pull Request**
```bash
# Create PR from main to test on GitHub
# After approval, merge PR
# Deployment runs automatically
```

### Monitor Deployment:

1. Go to **GitHub → Actions**
2. Click on latest workflow run
3. View logs for each job

### Manual Deployment:

If automatic deployment fails, deploy manually:

```bash
# SSH to test server
ssh ubuntu@test-server

# Pull latest code
cd /home/ubuntu/aaip-data
git pull origin test

# Update backend
cd backend
pip3 install -r requirements.txt
sudo systemctl restart aaip-backend-test

# Update frontend
cd ../frontend
npm ci
npm run build
sudo cp -r dist/* /var/www/aaip-test/

# Update scraper
cd ../scraper
pip3 install -r requirements.txt
```

## Rollback

If deployment causes issues:

```bash
ssh ubuntu@test-server
cd /home/ubuntu/aaip-data

# Rollback to previous commit
git log --oneline -5  # Find commit hash
git checkout <previous-commit-hash>

# Restart services
sudo systemctl restart aaip-backend-test
cd frontend && npm run build && sudo cp -r dist/* /var/www/aaip-test/
```

## Testing the Pipeline

### Test without deploying:
```bash
# Create a feature branch from test
git checkout test
git checkout -b test-feature
# Make changes
git push origin test-feature

# This will run tests but NOT deploy
```

### Test deployment:
```bash
git checkout test
git merge test-feature
git push origin test
# This will test AND deploy
```

## Notifications (Optional)

Add Slack/Discord webhook notification:

Add to workflow after deploy job:
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Test deployment ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Troubleshooting

### SSH connection fails:
- Verify SSH key is added to GitHub secrets
- Check server SSH access: `ssh ubuntu@test-server`
- Verify known_hosts

### Health check fails:
- Check if services are running: `systemctl status aaip-backend-test`
- Check ports are open: `netstat -tulpn | grep -E '8000|3002'`
- Check nginx: `sudo nginx -t`

### Build fails:
- Check Node.js version on server
- Clear npm cache: `npm cache clean --force`
- Check disk space: `df -h`

## Security Notes

⚠️ **Important:**
- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate SSH keys regularly
- Use separate database for test environment
- Restrict test server access

## Production Deployment

For production, create similar workflow:
- `.github/workflows/prod-deploy.yml`
- Triggered by pushes to `production` branch
- Additional approval gates
- Blue-green deployment
- Database migrations

See `PRODUCTION_DEPLOY.md` (to be created)
