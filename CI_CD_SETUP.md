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

### Database
- `TEST_DATABASE_URL`
  ```
  postgresql://randy:password@test-db-host:5432/aaip_data_test
  ```

### SSH Access (for deployment)
- `TEST_SERVER_SSH_KEY` - Private SSH key for test server
- `TEST_SERVER_HOST` - Test server IP/hostname (e.g., `100.77.247.113`)
- `TEST_SERVER_USER` - SSH username (e.g., `ubuntu` or `deployer`)

### Deployment Paths
- `TEST_DEPLOY_PATH` - Path on server where code is deployed
  ```
  /home/ubuntu/aaip-data
  ```

### Health Check URLs
- `TEST_BACKEND_URL` - Backend health check URL
  ```
  http://test-server.example.com:8000
  ```
- `TEST_FRONTEND_URL` - Frontend URL
  ```
  http://test-server.example.com:3002
  ```

## Test Server Setup

### Prerequisites on Test Server:

1. **Git repository cloned:**
```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/aaip-data.git
cd aaip-data
git checkout test
```

2. **Python environment:**
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r scraper/requirements.txt
pip3 install -r backend/requirements.txt
```

3. **Node.js:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

4. **Backend service (systemd):**
Create `/etc/systemd/system/aaip-backend-test.service`:
```ini
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

Enable and start:
```bash
sudo systemctl enable aaip-backend-test
sudo systemctl start aaip-backend-test
```

5. **Frontend web server (nginx):**
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

6. **SSH key for deployment:**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/aaip_deploy

# Copy public key to test server
ssh-copy-id -i ~/.ssh/aaip_deploy.pub ubuntu@test-server

# Add private key to GitHub Secrets
cat ~/.ssh/aaip_deploy
# Copy output and add as TEST_SERVER_SSH_KEY secret
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
