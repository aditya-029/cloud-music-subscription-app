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

export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo ""
echo "Checking backend health dependencies..."
python3 -m database.verify_database

echo ""
echo "Checking Gunicorn executable..."
if ! command -v gunicorn >/dev/null 2>&1; then
  echo "Gunicorn command not found. Installing again for current user..."
  python3 -m pip install --user gunicorn
fi

gunicorn --version

echo ""
echo "Stopping any existing Gunicorn process..."
sudo pkill -f "gunicorn.*backend.app:app" || true

echo ""
echo "Starting backend with Gunicorn on port 80..."

sudo env \
  PATH="$PATH" \
  PYTHONPATH="$PYTHONPATH" \
  HOME="$HOME" \
  gunicorn \
  --workers 2 \
  --bind 0.0.0.0:80 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  backend.app:app