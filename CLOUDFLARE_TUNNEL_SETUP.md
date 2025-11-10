# Cloudflare Tunnel Setup for CI/CD

## Current Tunnel Information
- **Tunnel ID**: `39b2663b-cc31-48df-a461-9aaa5dd00137`
- **Tunnel Name**: `randy_workstation_at_home`
- **Config File**: `~/.cloudflared/config.yml`

## Problem: SSH Access Through Tunnel

Your current config only exposes HTTP services. To enable SSH through the tunnel, you need to add an SSH ingress rule.

## Solution 1: Add SSH Ingress to Your Tunnel (Recommended)

### Step 1: Update your `~/.cloudflared/config.yml`:

```yaml
tunnel: 39b2663b-cc31-48df-a461-9aaa5dd00137
credentials-file: /home/randy/.cloudflared/39b2663b-cc31-48df-a461-9aaa5dd00137.json

ingress:
  # SSH Access
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22
  
  # Existing HTTP service
  - hostname: glaze.randy.it.com
    service: http://localhost:80
  
  # Catch-all rule (must be last)
  - service: http_status:404
```

### Step 2: Add DNS Record in Cloudflare Dashboard

1. Go to **Cloudflare Dashboard** → Your Domain → **DNS**
2. Add a **CNAME** record:
   - **Name**: `ssh`
   - **Target**: `39b2663b-cc31-48df-a461-9aaa5dd00137.cfargotunnel.com`
   - **Proxy**: Enabled (orange cloud)

### Step 3: Restart Cloudflared

```bash
sudo systemctl restart cloudflared
# OR if running manually:
cloudflared tunnel run randy_workstation_at_home
```

### Step 4: Test SSH Access Locally

```bash
# Install cloudflared on your local machine
brew install cloudflare/cloudflare/cloudflared  # macOS
# OR
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Test SSH connection
cloudflared access ssh --hostname ssh.randy.it.com
# OR add to ~/.ssh/config:
Host randy-workstation
    HostName ssh.randy.it.com
    User jinzhiqiang
    ProxyCommand cloudflared access ssh --hostname %h
```

## Solution 2: Use Cloudflare Access + Service Token (Alternative)

If you don't want to modify the tunnel ingress:

### Step 1: Create an Access Application

1. Go to **Cloudflare Zero Trust** → **Access** → **Applications**
2. **Add an application** → **Self-hosted**
3. **Application name**: `Randy Workstation SSH`
4. **Application domain**: `ssh.randy.it.com`
5. **Type**: SSH
6. **Session duration**: Choose (e.g., 24 hours)
7. **Policies**: 
   - Add **Service Auth** policy
   - Allow **Service Token** (create one in **Access** → **Service Auth**)

### Step 2: Get Service Token

1. **Zero Trust** → **Access** → **Service Auth** → **Create Service Token**
2. Save the **Client ID** and **Client Secret**
3. Add to GitHub Secrets:
   - `CF_SERVICE_CLIENT_ID`: Your client ID
   - `CF_SERVICE_CLIENT_SECRET`: Your client secret

## GitHub Secrets Required

Add these in **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**:

```
✅ CF_TUNNEL_ID=39b2663b-cc31-48df-a461-9aaa5dd00137
✅ CF_SSH_HOST=ssh.randy.it.com
✅ SSH_USER=jinzhiqiang
✅ TEST_DEPLOY_PATH=/Users/jinzhiqiang/workspaces/doit/aaip-data
✅ TEST_DATABASE_URL=postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db
✅ PROD_DATABASE_URL=postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db
✅ TEST_BACKEND_URL=http://localhost:8000
✅ TEST_FRONTEND_URL=http://localhost:3002

# Optional - if using Solution 2:
CF_SERVICE_CLIENT_ID=your-service-token-client-id
CF_SERVICE_CLIENT_SECRET=your-service-token-secret
```

## Database Connection Issue

### Problem:
When running scraper in GitHub Actions, it tries to connect to `localhost:5432` instead of your remote DB.

### Root Cause:
The scraper doesn't have `DATABASE_URL` environment variable set, so it defaults to localhost.

### Solution (Already Fixed):
In `test-deploy.yml`, line 52:
```yaml
- name: Test scraper
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}  # ✅ This sets the DB URL
  run: |
    cd scraper
    python3 -c "import scraper_enhanced; print('Scraper module loaded successfully')"
```

Make sure you set `TEST_DATABASE_URL` secret to:
```
postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db
```

## Why Cloudflared Installs Every Time

### Answer: It Doesn't (After This Fix)!

The workflow now has **caching** (lines 83-88):

```yaml
- name: 💾 Cache cloudflared CLI
  id: cache-cloudflared
  uses: actions/cache@v3
  with:
    path: /usr/local/bin/cloudflared
    key: cloudflared-${{ runner.os }}-latest
    
- name: 🛠️ Install cloudflared CLI
  if: steps.cache-cloudflared.outputs.cache-hit != 'true'  # ✅ Only if not cached
  run: ...
```

**First run**: Downloads and installs cloudflared  
**Subsequent runs**: Uses cached version (faster!)

## Testing Your Setup

### 1. Test Tunnel is Running:
```bash
# On your workstation
cloudflared tunnel info randy_workstation_at_home
# Should show: CONNECTIONS: 4 (multiple edge locations)
```

### 2. Test SSH Through Tunnel:
```bash
# From another machine
ssh -o ProxyCommand="cloudflared access ssh --hostname ssh.randy.it.com" jinzhiqiang@ssh.randy.it.com
```

### 3. Test GitHub Action:
- Push a commit to `test` branch
- Check GitHub Actions logs
- Should see: "✅ Using cached cloudflared CLI"

## Troubleshooting

### Issue: "dial tcp: lookup ssh.randy.it.com: no such host"
**Solution**: Add the DNS CNAME record (see Step 2 in Solution 1)

### Issue: "connection refused"
**Solution**: Make sure cloudflared tunnel is running on your workstation:
```bash
sudo systemctl status cloudflared
# OR restart:
sudo systemctl restart cloudflared
```

### Issue: "Authentication failed"
**Solution**: 
- Option A: Use tunnel ingress (Solution 1) - no auth needed
- Option B: Set up Access application + service token (Solution 2)

## Recommended Approach

**Use Solution 1** (Tunnel Ingress) - It's simpler:
1. ✅ No authentication needed
2. ✅ Direct SSH access through tunnel
3. ✅ Works with existing tunnel
4. ✅ Just add ingress rule + DNS record

**Solution 2** is more complex and requires Cloudflare Zero Trust Access setup.

## Next Steps

1. **Update tunnel config** with SSH ingress rule
2. **Add DNS record** for `ssh.randy.it.com`
3. **Restart cloudflared** on workstation
4. **Test SSH connection** locally first
5. **Set all GitHub secrets** listed above
6. **Push to test branch** to trigger deployment

---

Need help? Check the logs:
- Workstation: `sudo journalctl -u cloudflared -f`
- GitHub Actions: Repository → Actions → Latest workflow run
