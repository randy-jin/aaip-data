#!/bin/bash
# Setup script for aaip-backend-test systemd service
# Run this on the server as the deploy user (randy)

set -e

echo "🚀 Setting up aaip-backend-test systemd service..."

# Copy service file to systemd directory
echo "📋 Copying service file..."
sudo cp /home/randy/aaip-data/deployment/aaip-backend-test.service /etc/systemd/system/

# Set correct permissions
echo "🔒 Setting permissions..."
sudo chmod 644 /etc/systemd/system/aaip-backend-test.service

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service to start on boot
echo "✅ Enabling service..."
sudo systemctl enable aaip-backend-test

# Start the service
echo "▶️  Starting service..."
sudo systemctl start aaip-backend-test

# Check status
echo ""
echo "📊 Service status:"
sudo systemctl status aaip-backend-test --no-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "Useful commands:"
echo "  - Check status:  sudo systemctl status aaip-backend-test"
echo "  - View logs:     sudo journalctl -u aaip-backend-test -f"
echo "  - Restart:       sudo systemctl restart aaip-backend-test"
echo "  - Stop:          sudo systemctl stop aaip-backend-test"
