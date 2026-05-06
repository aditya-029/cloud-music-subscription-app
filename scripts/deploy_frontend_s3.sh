#!/bin/bash

set -e

# =========================================================
# Deploy React Frontend to S3 Static Website Hosting
# Run from project root:
#   ./scripts/deploy_frontend_s3.sh
#
# Optional:
#   VITE_API_BASE_URL=http://your-backend-url ./scripts/deploy_frontend_s3.sh
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_ROOT"

echo "========================================================="
echo "Deploying React frontend to S3"
echo "========================================================="

echo ""
echo "Step 1: Checking AWS credentials..."
aws sts get-caller-identity > /dev/null
echo "AWS credentials are valid."

echo ""
echo "Step 2: Checking AWS region..."
aws configure set region "$AWS_REGION"
echo "Using AWS region: $AWS_REGION"

echo ""
echo "Step 3: Preparing frontend environment..."

if [ -n "$VITE_API_BASE_URL" ]; then
  echo "Using supplied VITE_API_BASE_URL: $VITE_API_BASE_URL"
  cat > frontend/.env.production <<EOF
VITE_API_BASE_URL=$VITE_API_BASE_URL
EOF
else
  echo "No VITE_API_BASE_URL supplied."
  echo "Using frontend/.env if available, otherwise Vite fallback/defaults."
fi

echo ""
echo "Step 4: Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "Step 5: Building React frontend..."
npm run build

if [ ! -d "dist" ]; then
  echo "ERROR: frontend/dist was not created."
  exit 1
fi

cd "$PROJECT_ROOT"

echo ""
echo "Step 6: Creating S3 bucket if needed..."

if aws s3api head-bucket --bucket "$FRONTEND_BUCKET" 2>/dev/null; then
  echo "Frontend bucket already exists: $FRONTEND_BUCKET"
else
  echo "Creating frontend bucket: $FRONTEND_BUCKET"

  if [ "$AWS_REGION" = "us-east-1" ]; then
    aws s3api create-bucket \
      --bucket "$FRONTEND_BUCKET" \
      --region "$AWS_REGION"
  else
    aws s3api create-bucket \
      --bucket "$FRONTEND_BUCKET" \
      --region "$AWS_REGION" \
      --create-bucket-configuration LocationConstraint="$AWS_REGION"
  fi

  echo "Bucket created: $FRONTEND_BUCKET"
fi

echo ""
echo "Step 7: Disabling S3 block public access for frontend bucket..."
aws s3api put-public-access-block \
  --bucket "$FRONTEND_BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

echo ""
echo "Step 8: Enabling S3 static website hosting..."
aws s3 website "s3://$FRONTEND_BUCKET" \
  --index-document index.html \
  --error-document index.html

echo ""
echo "Step 9: Applying bucket policy for public static frontend access..."

cat > /tmp/cloud-music-frontend-bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadForStaticFrontend",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$FRONTEND_BUCKET/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket "$FRONTEND_BUCKET" \
  --policy file:///tmp/cloud-music-frontend-bucket-policy.json

echo ""
echo "Step 10: Uploading frontend build to S3..."
aws s3 sync frontend/dist/ "s3://$FRONTEND_BUCKET/" \
  --delete \
  --cache-control "no-cache"

echo ""
echo "========================================================="
echo "Frontend deployment complete."
echo "Frontend URL:"
echo "$FRONTEND_WEBSITE_URL"
echo "========================================================="
echo ""
echo "Note:"
echo "If the frontend loads but login/search fails, update VITE_API_BASE_URL"
echo "to a deployed backend URL and rerun this script."