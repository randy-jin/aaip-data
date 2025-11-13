# Frontend Access Setup Guide

This guide shows you how to access your AAIP Data Tracker frontend through Cloudflare Tunnel.

## Architecture

```
Internet
   ↓
Cloudflare Tunnel (aaip.randy.it.com)
   ↓
Nginx (localhost:80)
   ↓
   ├── Frontend: /var/www/aaip-test/ (Static files)
   └── Backend API: localhost:8000 (FastAPI)
```

## Step 1: Install and Configure Nginx

### 1.1 Install Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

### 1.2 Install the configuration file

```bash
# Copy Nginx config
sudo cp /home/randy/deploy/aaip-data/deployment/nginx-aaip-test.conf /etc/nginx/sites-available/aaip-test

# Enable the site
sudo ln -s /etc/nginx/sites-available/aaip-test /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 1.3 Verify Nginx is running

```bash
sudo systemctl status nginx
curl http://localhost/
```

## Step 2: Update Cloudflare Tunnel Configuration

You need to add a new hostname to your Cloudflare Tunnel to expose the frontend.

### 2.1 Edit Cloudflare Tunnel config

```bash
sudo nano ~/.cloudflared/config.yml
```

Add a new ingress rule for the frontend (before the 404 catch-all):

```yaml
tunnel: 39b2663b-cc31-48df-a461-9aaa5dd00137
credentials-file: /home/randy/.cloudflared/39b2663b-cc31-48df-a461-9aaa5dd00137.json

ingress:
  # Existing glaze service
  - hostname: glaze.randy.it.com
    service: http://localhost:80

  # SSH access
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22

  # NEW: AAIP Test Frontend
  - hostname: aaip-test.randy.it.com
    service: http://localhost:80

  # Catch-all (must be last)
  - service: http_status:404
```

### 2.2 Restart Cloudflare Tunnel

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

## Step 3: Configure DNS in Cloudflare Dashboard

1. Go to **Cloudflare Dashboard** → **Zero Trust** → **Access** → **Tunnels**
2. Click on your tunnel: `randy_workstation_at_home`
3. Go to **Public Hostname** tab
4. Click **Add a public hostname**
5. Configure:
   - **Subdomain**: `aaip-test`
   - **Domain**: `randy.it.com`
   - **Service Type**: `HTTP`
   - **URL**: `localhost:80`
6. Click **Save hostname**

**OR** if you prefer command line:

```bash
cloudflared tunnel route dns randy_workstation_at_home aaip-test.randy.it.com
```

## Step 4: Update Frontend API Configuration

The frontend needs to know the backend API URL. Update the API base URL:

### Option A: Use environment variable (recommended)

Edit the systemd service file to pass API URL:

```bash
sudo nano /etc/systemd/system/aaip-backend-test.service
```

Add this line in the `[Service]` section:
```ini
Environment="CORS_ORIGINS=https://aaip-test.randy.it.com"
```

Then restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-backend-test
```

### Option B: Update frontend source code

Edit `frontend/src/api.js` to use the correct API endpoint based on environment.

## Step 5: Test Access

### 5.1 Local testing

```bash
# Test frontend
curl http://localhost/

# Test backend API through Nginx
curl http://localhost/api/stats
```

### 5.2 External testing

Open your browser and visit:
```
https://aaip-test.randy.it.com
```

You should see the AAIP Data Tracker frontend!

## Step 6: Optional - Add HTTPS (Cloudflare handles this automatically)

Cloudflare Tunnel automatically provides HTTPS for your frontend. No additional configuration needed!

## Troubleshooting

### Frontend shows "Failed to fetch data"

This usually means the API is not accessible. Check:

```bash
# 1. Backend service is running
sudo systemctl status aaip-backend-test

# 2. Backend is listening on port 8000
curl http://localhost:8000/api/stats

# 3. Nginx proxy is working
curl http://localhost/api/stats

# 4. Check Nginx logs
sudo tail -f /var/log/nginx/aaip-test-error.log
```

### Can't access via Cloudflare URL

```bash
# Check tunnel status
sudo systemctl status cloudflared

# Check tunnel logs
sudo journalctl -u cloudflared -n 50

# Verify DNS is configured
dig aaip-test.randy.it.com

# Test from server
curl https://aaip-test.randy.it.com
```

### Nginx errors

```bash
# Check Nginx config syntax
sudo nginx -t

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check if port 80 is in use
sudo lsof -i :80
```

### Permission issues

```bash
# Ensure web directory has correct permissions
sudo chown -R www-data:www-data /var/www/aaip-test/
sudo chmod -R 755 /var/www/aaip-test/

# Or if you want randy to own it:
sudo chown -R randy:randy /var/www/aaip-test/
```

## Alternative: Use Separate Ports

If you want to separate frontend and backend on different ports:

### Update `~/.cloudflared/config.yml`:

```yaml
ingress:
  # Frontend on separate subdomain
  - hostname: aaip-frontend.randy.it.com
    service: http://localhost:3000

  # Backend API on separate subdomain
  - hostname: aaip-api.randy.it.com
    service: http://localhost:8000

  # SSH
  - hostname: ssh.randy.it.com
    service: ssh://localhost:22

  - service: http_status:404
```

Then update frontend API base URL to point to `https://aaip-api.randy.it.com`.

## Summary of URLs

After setup, you'll have:

- **Frontend**: `https://aaip-test.randy.it.com`
- **Backend API**: `https://aaip-test.randy.it.com/api/`
- **SSH Access**: `ssh.randy.it.com` (via cloudflared)

## Security Considerations

1. **Cloudflare Access** (Optional): You can add authentication to your frontend:
   - Go to Cloudflare Zero Trust Dashboard
   - Create an Access Policy for `aaip-test.randy.it.com`
   - Add authentication rules (email, GitHub, etc.)

2. **Database Security**: Ensure PostgreSQL is not exposed externally

3. **Rate Limiting**: Consider adding Nginx rate limiting for API endpoints

4. **CORS**: Update backend CORS settings to only allow your frontend domain

## Useful Commands

```bash
# Restart all services
sudo systemctl restart aaip-backend-test
sudo systemctl restart nginx
sudo systemctl restart cloudflared

# View all logs
sudo journalctl -u aaip-backend-test -f
sudo tail -f /var/log/nginx/aaip-test-access.log
sudo journalctl -u cloudflared -f

# Check service status
sudo systemctl status aaip-backend-test nginx cloudflared
```
