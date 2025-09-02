#!/bin/bash

# Deploy Italian Address Service
# Usage: ./deploy.sh <IP_ADDRESS> <SSH_KEY_PATH>

if [ $# -ne 2 ]; then
    echo "❌ Usage: $0 <IP_ADDRESS> <SSH_KEY_PATH>"
    echo "   Example: $0 13.234.225.149 ~/.ssh/my-key.pem"
    exit 1
fi

SERVER_IP=$1
SSH_KEY=$2
SSH_USER="ubuntu"
DEPLOY_PORT=10000
ADMIN_TOKEN=$(openssl rand -hex 16)

echo "🚀 Deploying Italian Address Service"
echo "=================================="
echo "Server IP: $SERVER_IP"
echo "SSH Key: $SSH_KEY"
echo "SSH User: $SSH_USER"
echo "Port: $DEPLOY_PORT"
echo "Admin Token: $ADMIN_TOKEN"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    echo "Please provide the correct path to your SSH key"
    exit 1
fi

# Test SSH connection
echo "🔐 Testing SSH connection..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo "❌ SSH connection failed"
    echo "Please check:"
    echo "  1. SSH key path: $SSH_KEY"
    echo "  2. Server IP: $SERVER_IP"
    echo "  3. SSH user: $SSH_USER"
    echo "  4. Security group allows SSH (port 22)"
    exit 1
fi

echo "✅ SSH connection successful"

# Create deployment archive
echo "📦 Creating deployment package..."
tar -czf italian-address-service.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='*.pyc' \
    --exclude='.env' \
    .

# Copy files to server
echo "📤 Copying files to server..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no italian-address-service.tar.gz "$SSH_USER@$SERVER_IP:~/"

# Deploy on server
echo "🏗️ Installing and starting service..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << EOF
set -e

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker \$USER
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Extract and setup application
rm -rf italian-address-service
tar -xzf italian-address-service.tar.gz
cd italian-address-service

# Stop any existing services and clean up
docker-compose down 2>/dev/null || true

# Update docker-compose for production port
sed -i "s/- \"10000:8000\"/- \"$DEPLOY_PORT:8000\"/" docker-compose.yml

# Build and start services
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Seed the database
echo "🌱 Seeding database with Italian address data..."
for i in {1..5}; do
    if curl -X POST "http://localhost:$DEPLOY_PORT/datasets/seed" \
       -H "X-Admin-Token: changeme" \
       -H "Content-Type: application/json" > /dev/null 2>&1; then
        echo "✅ Database seeded successfully!"
        break
    else
        echo "⏳ Attempt \$i failed, retrying..."
        sleep 5
    fi
done

# Test the service
echo "🧪 Testing service..."
TEST_RESULT=\$(curl -X POST "http://localhost:$DEPLOY_PORT/normalize" \
  -H "Content-Type: application/json" \
  -d '{"address": "Via del Corso 123, Rome"}' -s 2>/dev/null || echo "FAILED")

if [[ "\$TEST_RESULT" == *"formatted"* ]]; then
    echo "✅ Service is working correctly!"
else
    echo "⚠️ Service test failed"
fi

EOF

# Clean up local archive
rm italian-address-service.tar.gz

echo ""
echo "🎉 Deployment completed!"
echo "=================================="
echo ""
echo "🌐 Your service is ready:"
echo "   Web UI: http://$SERVER_IP:$DEPLOY_PORT/"
echo "   API Docs: http://$SERVER_IP:$DEPLOY_PORT/docs"
echo ""
echo "🧪 Test it:"
echo "   curl -X POST \"http://$SERVER_IP:$DEPLOY_PORT/normalize\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"address\": \"Via del Corso 123, Rome\"}'"
echo ""
echo "📊 Management:"
echo "   ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd italian-address-service && docker-compose logs -f'"
echo ""