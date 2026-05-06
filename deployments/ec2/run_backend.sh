#!/bin/bash

set -e

# =========================================================
# EC2 Backend Run Script
# Run this script INSIDE the EC2 instance from project root:
#   chmod +x deployments/ec2/run_backend.sh
#   ./deployments/ec2/run_backend.sh
#
# The backend is exposed on HTTP port 80 for assignment compliance.
# =========================================================

echo "========================================================="
echo "Starting Cloud Music Backend on EC2"
echo "========================================================="

if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found."
  echo "Run ./deployments/ec2/setup_ec2.sh first."
  exit 1
fi

echo ""
echo "Checking backend health dependencies..."
python3 -m database.verify_database

echo ""
echo "Stopping any existing Gunicorn process..."
sudo pkill -f "gunicorn.*backend.app:app" || true

echo ""
echo "Starting backend with Gunicorn on port 80..."

sudo python3 -m gunicorn \
  --workers 2 \
  --bind 0.0.0.0:80 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  backend.app:app