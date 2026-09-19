#!/bin/bash
# ============================================================================
# Turnkey EC2 UserData / Bootstrap Deployment Script (Ubuntu 22.04 / 24.04 LTS)
# Team infinity — Intelligent Ambulance Priority Management System
# ============================================================================

set -e

echo ">>> [1/5] Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git

echo ">>> [2/5] Installing Docker and Docker Compose..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER || true

echo ">>> [3/5] Cloning repository from GitHub..."
cd /home/ubuntu
if [ -d "smart-signal-ambulance-priority" ]; then
    cd smart-signal-ambulance-priority
    git pull origin main
else
    git clone https://github.com/404stephenFound/smart-signal-ambulance-priority.git
    cd smart-signal-ambulance-priority
fi

echo ">>> [4/5] Building and launching Docker container..."
sudo docker-compose down || true
sudo docker-compose up --build -d

echo ">>> [5/5] Verifying service health..."
sleep 5
curl -f http://localhost:8000/health || echo "Waiting for backend to finish startup..."

echo "======================================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "• Dashboard URL: http://$(curl -s http://checkip.amazonaws.com):8000"
echo "• Ambulance HUD: http://$(curl -s http://checkip.amazonaws.com):8000/ambulance"
echo "======================================================="
