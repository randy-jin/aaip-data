# Cloudflare Tunnel SSH Setup for CI/CD

## Current Status
Your Cloudflare Tunnel `randy_workstation_at_home` (ID: `39b2663b-cc31-48df-a461-9aaa5dd00137`) is configured but needs SSH access added for CI/CD deployment.

## Option 1: Add SSH to Your Tunnel (Quick Fix)

### Step 1: Update Tunnel Configuration

On your workstation, edit `~/.cloudflared/config.yml`:

```yaml
tunnel: 39b2663b-cc31-48df-a461-9aaa5dd00137
credentials-file: /home/randy/.cloudflared/39b2663b-cc31-48df-a461-9aaa5dd00137.json

ingress:
  - hostname: glaze.randy.it.com
    service: http://localhost:80
  # Add SSH support (catch-all)
  - service: ssh://localhost:22
```

### Step 2: Restart Cloudflared

```bash
# If running as systemd service
sudo systemctl restart cloudflared

# OR if running manually
cloudflared tunnel run randy_workstation_at_home
```

### Step 3: Test SSH Connection

From another machine:
```bash
cloudflared access ssh --hostname 39b2663b-cc31-48df-a461-9aaa5dd00137.cfargotunnel.com
```

### Step 4: GitHub Secrets

Set these secrets in GitHub → Settings → Secrets:

- `CF_TUNNEL_ID`: `39b2663b-cc31-48df-a461-9aaa5dd00137`
- `SSH_USER`: `jinzhiqiang` (or randy, whichever you use)
- `TEST_DEPLOY_PATH`: `/Users/jinzhiqiang/workspaces/doit/aaip-data`

## Option 2: GitHub Self-Hosted Runner (Recommended)

**This is simpler and more reliable for local deployments!**

### Why Self-Hosted Runner?

✅ No SSH configuration needed  
✅ No Cloudflare Access setup  
✅ Runs directly on your workstation  
✅ Faster deployment  
✅ Easier to debug  

### Setup Instructions

1. **Get Runner Token**
   - Go to: `https://github.com/YOUR_USERNAME/aaip-data/settings/actions/runners/new`
   - Copy the token

2. **Install Runner on Your Workstation**

```bash
# Create runner directory
cd ~
mkdir actions-runner && cd actions-runner

# Download runner (for Linux)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure (replace TOKEN with your token from step 1)
./config.sh --url https://github.com/YOUR_USERNAME/aaip-data --token YOUR_TOKEN

# Install and start as service
sudo ./svc.sh install
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

3. **Update Workflow**

Change `.github/workflows/test-deploy.yml`:

```yaml
deploy:
  name: Deploy to Test Server
  needs: test
  runs-on: self-hosted  # Changed from ubuntu-latest
```

4. **Remove SSH Steps**

You won't need:
- Install cloudflared
- Configure SSH
- ssh cf-tunnel commands

Just use direct commands:
```yaml
- name: Deploy Backend
  run: |
    cd ${{ secrets.TEST_DEPLOY_PATH }}
    git pull origin test
    cd backend
    pip3 install -r requirements.txt
    sudo systemctl restart aaip-backend-test
```

## Option 3: Add SSH with Hostname (Advanced)

If you want SSH via hostname like `ssh.randy.it.com`:

1. **Update tunnel config:**
```yaml
ingress:
  - hostname: glaze.randy.it.com
    service: http://localhost:80
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22
  - service: http_status:404
```

2. **Add DNS record in Cloudflare:**
   - Type: CNAME
   - Name: `ssh`
   - Target: `39b2663b-cc31-48df-a461-9aaa5dd00137.cfargotunnel.com`
   - Proxy: On

3. **Add GitHub secret:**
   - `CF_SSH_HOSTNAME`: `ssh.randy.it.com`

## Troubleshooting

### SSH Connection Refused
- Make sure SSH server is running: `sudo systemctl status sshd`
- Check firewall allows local connections: `sudo ufw status`

### Cloudflared Not Found
- Verify installation: `cloudflared --version`
- Check service status: `sudo systemctl status cloudflared`

### Permission Denied
- Ensure your user can SSH: `ssh localhost`
- Check `~/.ssh/authorized_keys` permissions

## Database Issue in Scraper.yml

The scraper workflow is trying to connect to `localhost` instead of your actual database. This is because:

1. The scraper runs on GitHub's servers
2. It can't connect to your local database

**Fix:** The scraper workflow should only test imports, not actual scraping:

```yaml
- name: Run enhanced scraper
  env:
    DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
  run: |
    cd scraper
    # Only test imports, don't actually scrape in CI
    python3 -c "import scraper_enhanced; print('✅ Scraper module OK')"
```

The actual scraping should run on your workstation via cron or systemd timer, where it has database access.

## Recommended Solution

**Use GitHub Self-Hosted Runner (Option 2)**

It's the simplest, most reliable solution for CI/CD to your local workstation. You avoid all the SSH and Cloudflare complexity.
