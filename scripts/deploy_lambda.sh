#!/bin/bash

set -e

# =========================================================
# Deploy Native Lambda Backend
# Run from project root:
#   ./scripts/deploy_lambda.sh
#
# This deploys the Lambda function only.
# API Gateway is deployed separately.
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_ROOT"

echo "========================================================="
echo "Cloud Music Native Lambda Backend Deployment"
echo "========================================================="

echo ""
echo "Step 1: Checking AWS credentials..."
aws sts get-caller-identity > /dev/null
echo "AWS credentials are valid."

echo ""
echo "Step 2: Getting AWS account ID and LabRole ARN..."
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
LAB_ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$LAB_ROLE_NAME"

echo "Account ID: $ACCOUNT_ID"
echo "LabRole ARN: $LAB_ROLE_ARN"

echo ""
echo "Step 3: Packaging Lambda backend..."
./scripts/package_lambda.sh

if [ ! -f "$LAMBDA_PACKAGE_NAME" ]; then
  echo "ERROR: Lambda package not found: $LAMBDA_PACKAGE_NAME"
  exit 1
fi

# AWS_REGION is reserved by Lambda and must not be manually set.
LAMBDA_ENVIRONMENT="Variables={
  LOGIN_TABLE=$LOGIN_TABLE,
  MUSIC_TABLE=$MUSIC_TABLE,
  SUBSCRIPTIONS_TABLE=$SUBSCRIPTIONS_TABLE,
  MUSIC_TITLE_INDEX=$MUSIC_TITLE_INDEX,
  MUSIC_YEAR_ALBUM_INDEX=$MUSIC_YEAR_ALBUM_INDEX,
  CORS_ORIGINS=*,
  S3_BUCKET_NAME=$ARTIST_IMAGE_BUCKET,
  S3_IMAGE_PREFIX=$S3_IMAGE_PREFIX
}"

echo ""
echo "Step 4: Creating or updating Lambda function..."

if aws lambda get-function \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" > /dev/null 2>&1; then

  echo "Lambda function already exists. Updating code..."

  aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --zip-file "fileb://$LAMBDA_PACKAGE_NAME" \
    --region "$AWS_REGION" > /dev/null

  aws lambda wait function-updated \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION"

  echo "Updating Lambda configuration..."

  aws lambda update-function-configuration \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --runtime python3.12 \
    --handler lambda_function.lambda_handler \
    --timeout 30 \
    --memory-size 512 \
    --role "$LAB_ROLE_ARN" \
    --environment "$LAMBDA_ENVIRONMENT" \
    --region "$AWS_REGION" > /dev/null

  aws lambda wait function-updated \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION"

else

  echo "Creating Lambda function..."

  aws lambda create-function \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --runtime python3.12 \
    --role "$LAB_ROLE_ARN" \
    --handler lambda_function.lambda_handler \
    --zip-file "fileb://$LAMBDA_PACKAGE_NAME" \
    --timeout 30 \
    --memory-size 512 \
    --environment "$LAMBDA_ENVIRONMENT" \
    --region "$AWS_REGION" > /dev/null

  aws lambda wait function-active \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION"

fi

echo ""
echo "Step 5: Running direct Lambda invoke health test..."

cat > /tmp/cloud-music-lambda-health-event.json <<'EOF'
{
  "httpMethod": "GET",
  "path": "/health",
  "headers": {},
  "queryStringParameters": null,
  "body": null,
  "isBase64Encoded": false
}
EOF

aws lambda invoke \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --payload fileb:///tmp/cloud-music-lambda-health-event.json \
  --region "$AWS_REGION" \
  /tmp/cloud-music-lambda-health-response.json > /tmp/cloud-music-lambda-invoke-meta.json

cat /tmp/cloud-music-lambda-health-response.json
echo ""

if grep -q '"success": true' /tmp/cloud-music-lambda-health-response.json; then
  echo "Direct Lambda health test passed."
else
  echo "WARNING: Direct Lambda health test did not return success=true."
  echo "Invoke metadata:"
  cat /tmp/cloud-music-lambda-invoke-meta.json
  echo ""
fi

echo ""
echo "========================================================="
echo "Lambda backend deployment complete."
echo "Function name:"
echo "$LAMBDA_FUNCTION_NAME"
echo ""
echo "Next step:"
echo "  ./scripts/deploy_api_gateway.sh"
echo "========================================================="