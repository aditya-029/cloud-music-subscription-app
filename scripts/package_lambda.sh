#!/bin/bash

set -e

# =========================================================
# Package Native Lambda Backend
# Run from project root:
#   ./scripts/package_lambda.sh
#
# Uses Docker so dependencies are installed for Linux/Lambda,
# not macOS.
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_ROOT"

echo "========================================================="
echo "Packaging Cloud Music Native Lambda Backend"
echo "========================================================="

echo ""
echo "Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
  echo "ERROR: Docker is not running."
  echo "Start Docker Desktop and rerun this script."
  exit 1
fi
echo "Docker is running."

echo ""
echo "Step 2: Cleaning old Lambda build artifacts..."
rm -rf lambda_build
rm -f "$LAMBDA_PACKAGE_NAME"

mkdir -p lambda_build

echo ""
echo "Step 3: Creating Lambda-only requirements file..."

cat > /tmp/cloud-music-lambda-requirements.txt <<'EOF'
boto3
botocore
python-dotenv
requests
pydantic
EOF

echo ""
echo "Step 4: Installing Lambda dependencies using Linux Docker..."

docker run --rm \
  --platform linux/amd64 \
  -v "$PROJECT_ROOT":/var/task \
  -v /tmp/cloud-music-lambda-requirements.txt:/tmp/lambda-requirements.txt \
  -w /var/task \
  python:3.12-slim \
  bash -c "pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /tmp/lambda-requirements.txt -t lambda_build"

echo ""
echo "Step 5: Copying application source into lambda_build..."

cp deployments/lambda/lambda_function.py lambda_build/

mkdir -p lambda_build/backend
mkdir -p lambda_build/backend/services
mkdir -p lambda_build/backend/utils
mkdir -p lambda_build/database

cp backend/__init__.py lambda_build/backend/ 2>/dev/null || touch lambda_build/backend/__init__.py
cp backend/config.py lambda_build/backend/

cp backend/services/__init__.py lambda_build/backend/services/ 2>/dev/null || touch lambda_build/backend/services/__init__.py
cp backend/services/auth_service.py lambda_build/backend/services/
cp backend/services/dynamodb_service.py lambda_build/backend/services/
cp backend/services/music_service.py lambda_build/backend/services/
cp backend/services/s3_service.py lambda_build/backend/services/
cp backend/services/subscription_service.py lambda_build/backend/services/

cp backend/utils/__init__.py lambda_build/backend/utils/ 2>/dev/null || touch lambda_build/backend/utils/__init__.py
cp backend/utils/response.py lambda_build/backend/utils/ 2>/dev/null || true

cp database/__init__.py lambda_build/database/ 2>/dev/null || touch lambda_build/database/__init__.py
cp database/db_config.py lambda_build/database/ 2>/dev/null || true

echo ""
echo "Step 6: Removing unnecessary files from package..."

find lambda_build -name "__pycache__" -type d -prune -exec rm -rf {} +
find lambda_build -name "*.pyc" -type f -delete
find lambda_build -name "*.dist-info" -type d | head -n 5 > /dev/null || true

echo ""
echo "Step 7: Creating Lambda deployment zip..."

cd lambda_build
zip -r "../$LAMBDA_PACKAGE_NAME" . > /dev/null
cd "$PROJECT_ROOT"

echo ""
echo "Step 8: Verifying package..."

if [ ! -f "$LAMBDA_PACKAGE_NAME" ]; then
  echo "ERROR: Lambda package was not created."
  exit 1
fi

ls -lh "$LAMBDA_PACKAGE_NAME"

echo ""
echo "========================================================="
echo "Lambda package created successfully:"
echo "$LAMBDA_PACKAGE_NAME"
echo "========================================================="