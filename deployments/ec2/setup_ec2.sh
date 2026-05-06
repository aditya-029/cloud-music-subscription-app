#!/bin/bash

set -e

# =========================================================
# EC2 Backend Setup Script
# Run this script INSIDE the EC2 instance from project root:
#   chmod +x deployments/ec2/setup_ec2.sh
#   ./deployments/ec2/setup_ec2.sh
# =========================================================

echo "========================================================="
echo "Cloud Music Backend - EC2 Setup"
echo "========================================================="

PROJECT_DIR="$(pwd)"

echo ""
echo "Step 1: Updating system packages..."

if command -v yum >/dev/null 2>&1; then
  sudo yum update -y
  sudo yum install -y git python3 python3-pip
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y git python3 python3-pip
else
  echo "Unsupported Linux package manager. Install git, python3 and pip manually."
  exit 1
fi

echo ""
echo "Step 2: Upgrading pip..."
python3 -m pip install --upgrade pip

echo ""
echo "Step 3: Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "Step 4: Creating production .env file..."

cat > .env <<'EOF'
AWS_REGION=us-east-1

LOGIN_TABLE=login
MUSIC_TABLE=music
SUBSCRIPTIONS_TABLE=subscriptions

MUSIC_TITLE_INDEX=title-index
MUSIC_YEAR_ALBUM_INDEX=year-album-index

APP_HOST=0.0.0.0
APP_PORT=80
FLASK_DEBUG=False

CORS_ORIGINS=*

S3_BUCKET_NAME=cloud-music-app-s4097885-2026-a2
S3_IMAGE_PREFIX=artist-images/
EOF

echo ".env file created for EC2 deployment."

echo ""
echo "Step 5: Checking AWS identity from EC2 instance..."
aws sts get-caller-identity

echo ""
echo "Step 6: Verifying DynamoDB database setup..."
python3 -m database.verify_database

echo ""
echo "Step 7: Checking Gunicorn installation..."
python3 -m gunicorn --version

echo ""
echo "========================================================="
echo "EC2 backend setup complete."
echo "Project directory: $PROJECT_DIR"
echo ""
echo "Next step:"
echo "  ./deployments/ec2/run_backend.sh"
echo "========================================================="