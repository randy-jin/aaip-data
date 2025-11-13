# Server Deployment Setup Guide

This guide walks you through setting up the AAIP Data Tracker backend service on your Ubuntu server.

## Prerequisites

- Ubuntu 24.04 server
- PostgreSQL installed and running
- User `randy` with sudo privileges
- Repository cloned at `/home/randy/aaip-data`

## Step 1: Setup Backend Service

### 1.1 Install the systemd service file

```bash
# On the server, run:
cd /home/randy/aaip-data
git pull origin test  # Make sure you have latest deployment files

# Copy service file to systemd directory
sudo cp deployment/aaip-backend-test.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/aaip-backend-test.service
```

### 1.2 Configure environment variables (if needed)

Edit the service file to add any required environment variables:

```bash
sudo nano /etc/systemd/system/aaip-backend-test.service
```

Add environment variables in the `[Service]` section:
```ini
Environment="DATABASE_URL=postgresql://user:password@localhost/aaip_data"
Environment="OTHER_VAR=value"
```

### 1.3 Enable and start the service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable aaip-backend-test

# Start the service
sudo systemctl start aaip-backend-test

# Check status
sudo systemctl status aaip-backend-test
```

### 1.4 Verify the backend is running

```bash
# Check if the service is listening on port 8000
curl http://localhost:8000/api/stats

# View logs
sudo journalctl -u aaip-backend-test -n 50
```

## Step 2: Configure Sudoers for Automated Deployment

This allows GitHub Actions to restart the service without password prompts.

```bash
# Copy sudoers configuration
sudo cp deployment/aaip-deploy-sudoers /etc/sudoers.d/aaip-deploy

# Set correct permissions (MUST be 440)
sudo chmod 440 /etc/sudoers.d/aaip-deploy

# Validate syntax (IMPORTANT!)
sudo visudo -c
```

Expected output:
```
/etc/sudoers: parsed OK
/etc/sudoers.d/aaip-deploy: parsed OK
```

### 2.1 Test sudoers configuration

```bash
# Test service restart without password
sudo systemctl restart aaip-backend-test

# If it asks for password, the sudoers config is incorrect
```

## Step 3: Setup Frontend Web Directory

```bash
# Create web directory if it doesn't exist
sudo mkdir -p /var/www/aaip-test

# Set ownership to randy (or www-data, depending on your web server)
sudo chown randy:randy /var/www/aaip-test

# Or if using nginx/apache:
# sudo chown www-data:www-data /var/www/aaip-test
```

## Step 4: Setup Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE aaip_data;
CREATE USER aaip_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aaip_data TO aaip_user;
\q

# Initialize database schema
cd /home/randy/aaip-data/backend
source venv/bin/activate
python -c "from database_init import init_database; init_database()"
deactivate
```

## Step 5: Test Deployment Manually

Before running the GitHub Actions workflow, test the deployment steps manually:

```bash
cd /home/randy/aaip-data

# Pull latest code
git fetch origin
git checkout test
git pull origin test

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate

# Restart service
sudo systemctl restart aaip-backend-test

# Build frontend
cd ../frontend
npm ci --quiet
npm run build

# Deploy frontend
sudo cp -r dist/* /var/www/aaip-test/

# Update scraper
cd ../scraper
source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate

# Verify everything is running
sudo systemctl status aaip-backend-test
curl http://localhost:8000/api/stats
ls -la /var/www/aaip-test/
```

## Step 6: Verify GitHub Actions Can Connect

```bash
# On your local machine, trigger the workflow by pushing to test branch
git push origin test

# Watch GitHub Actions logs at:
# https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# On the server, monitor the deployment:
sudo journalctl -u aaip-backend-test -f
```

## Troubleshooting

### Service fails to start

```bash
# Check detailed logs
sudo journalctl -u aaip-backend-test -n 100 --no-pager

# Common issues:
# 1. Virtual environment not created
cd /home/randy/aaip-data/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 2. Database connection issues
# Check DATABASE_URL in service file

# 3. Port already in use
sudo lsof -i :8000
# Kill the process or change the port
```

### Sudo password still required

```bash
# Verify sudoers file syntax
sudo visudo -c

# Check file permissions
ls -la /etc/sudoers.d/aaip-deploy
# Should be: -r--r----- 1 root root

# Test specific command
sudo -n systemctl restart aaip-backend-test
# Should not ask for password
```

### Frontend not accessible

```bash
# Check if files were copied
ls -la /var/www/aaip-test/

# Check web server configuration (nginx example)
sudo nginx -t
sudo systemctl restart nginx

# Check permissions
sudo chown -R www-data:www-data /var/www/aaip-test/
```

## Useful Commands

```bash
# Service management
sudo systemctl status aaip-backend-test      # Check status
sudo systemctl restart aaip-backend-test     # Restart service
sudo systemctl stop aaip-backend-test        # Stop service
sudo systemctl start aaip-backend-test       # Start service

# View logs
sudo journalctl -u aaip-backend-test -f      # Follow logs in real-time
sudo journalctl -u aaip-backend-test -n 100  # Last 100 log lines
sudo journalctl -u aaip-backend-test --since "1 hour ago"  # Logs from last hour

# Test backend API
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/summary?limit=10

# Check listening ports
sudo lsof -i :8000
sudo netstat -tlnp | grep 8000
```

## Next Steps

Once everything is working:

1. Configure your web server (nginx/apache) to reverse proxy to the backend
2. Set up SSL certificates for HTTPS
3. Configure the scraper cron job to run periodically
4. Set up monitoring and alerting

## Security Checklist

- [ ] Database password is strong and stored securely
- [ ] SSH keys are properly secured (chmod 600)
- [ ] Sudoers file has correct permissions (440)
- [ ] Service runs as non-root user (randy)
- [ ] Firewall rules are configured properly
- [ ] Web server has appropriate security headers
- [ ] SSL/TLS certificates are configured
