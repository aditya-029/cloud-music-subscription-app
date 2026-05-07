#!/bin/bash

set -e

# =========================================================
# Deploy API Gateway for Native Lambda Backend
# Run from project root:
#   ./scripts/deploy_api_gateway.sh
#
# Creates/updates an HTTP API Gateway that routes all required
# backend endpoints to the Lambda function.
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_ROOT"

echo "========================================================="
echo "Cloud Music API Gateway Deployment"
echo "========================================================="

echo ""
echo "Step 1: Checking AWS credentials..."
aws sts get-caller-identity > /dev/null
echo "AWS credentials are valid."

echo ""
echo "Step 2: Getting AWS account ID..."
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
LAMBDA_ARN="arn:aws:lambda:$AWS_REGION:$ACCOUNT_ID:function:$LAMBDA_FUNCTION_NAME"

echo "Account ID: $ACCOUNT_ID"
echo "Lambda ARN: $LAMBDA_ARN"

echo ""
echo "Step 3: Checking Lambda function exists..."

aws lambda get-function \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" > /dev/null

echo "Lambda function found: $LAMBDA_FUNCTION_NAME"

echo ""
echo "Step 4: Creating or finding HTTP API Gateway..."

API_ID="$(aws apigatewayv2 get-apis \
  --region "$AWS_REGION" \
  --query "Items[?Name=='$API_GATEWAY_NAME'].ApiId | [0]" \
  --output text)"

if [ "$API_ID" = "None" ] || [ -z "$API_ID" ]; then
  API_ID="$(aws apigatewayv2 create-api \
    --name "$API_GATEWAY_NAME" \
    --protocol-type HTTP \
    --cors-configuration "AllowOrigins=*,AllowMethods=GET,POST,DELETE,OPTIONS,AllowHeaders=content-type,authorization,AllowCredentials=false,MaxAge=3600" \
    --region "$AWS_REGION" \
    --query "ApiId" \
    --output text)"

  echo "Created API Gateway: $API_ID"
else
  echo "API Gateway already exists: $API_ID"

  aws apigatewayv2 update-api \
    --api-id "$API_ID" \
    --cors-configuration "AllowOrigins=*,AllowMethods=GET,POST,DELETE,OPTIONS,AllowHeaders=content-type,authorization,AllowCredentials=false,MaxAge=3600" \
    --region "$AWS_REGION" > /dev/null

  echo "Updated API Gateway CORS configuration."
fi

echo ""
echo "Step 5: Creating or finding Lambda integration..."

INTEGRATION_ID="$(aws apigatewayv2 get-integrations \
  --api-id "$API_ID" \
  --region "$AWS_REGION" \
  --query "Items[?IntegrationUri=='$LAMBDA_ARN'].IntegrationId | [0]" \
  --output text)"

if [ "$INTEGRATION_ID" = "None" ] || [ -z "$INTEGRATION_ID" ]; then
  INTEGRATION_ID="$(aws apigatewayv2 create-integration \
    --api-id "$API_ID" \
    --integration-type AWS_PROXY \
    --integration-uri "$LAMBDA_ARN" \
    --payload-format-version "2.0" \
    --region "$AWS_REGION" \
    --query "IntegrationId" \
    --output text)"

  echo "Created Lambda integration: $INTEGRATION_ID"
else
  echo "Lambda integration already exists: $INTEGRATION_ID"
fi

echo ""
echo "Step 6: Creating required API routes..."

create_route_if_missing() {
  local ROUTE_KEY="$1"

  local EXISTING_ROUTE_ID
  EXISTING_ROUTE_ID="$(aws apigatewayv2 get-routes \
    --api-id "$API_ID" \
    --region "$AWS_REGION" \
    --query "Items[?RouteKey=='$ROUTE_KEY'].RouteId | [0]" \
    --output text)"

  if [ "$EXISTING_ROUTE_ID" = "None" ] || [ -z "$EXISTING_ROUTE_ID" ]; then
    aws apigatewayv2 create-route \
      --api-id "$API_ID" \
      --route-key "$ROUTE_KEY" \
      --target "integrations/$INTEGRATION_ID" \
      --region "$AWS_REGION" > /dev/null

    echo "Created route: $ROUTE_KEY"
  else
    echo "Route already exists: $ROUTE_KEY"
  fi
}

create_route_if_missing "GET /health"
create_route_if_missing "POST /login"
create_route_if_missing "POST /register"
create_route_if_missing "GET /songs"
create_route_if_missing "GET /subscriptions"
create_route_if_missing "POST /subscriptions"
create_route_if_missing "DELETE /subscriptions/{email}/{song_id}"
create_route_if_missing "OPTIONS /{proxy+}"

echo ""
echo "Step 7: Creating or updating default stage..."

STAGE_EXISTS="$(aws apigatewayv2 get-stages \
  --api-id "$API_ID" \
  --region "$AWS_REGION" \
  --query "Items[?StageName=='\$default'].StageName | [0]" \
  --output text)"

if [ "$STAGE_EXISTS" = "None" ] || [ -z "$STAGE_EXISTS" ]; then
  aws apigatewayv2 create-stage \
    --api-id "$API_ID" \
    --stage-name '$default' \
    --auto-deploy \
    --region "$AWS_REGION" > /dev/null

  echo "Created default stage."
else
  aws apigatewayv2 update-stage \
    --api-id "$API_ID" \
    --stage-name '$default' \
    --auto-deploy \
    --region "$AWS_REGION" > /dev/null

  echo "Updated default stage."
fi

echo ""
echo "Step 8: Adding Lambda invoke permission for API Gateway..."

STATEMENT_ID="ApiGatewayInvokePermission"

aws lambda remove-permission \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --statement-id "$STATEMENT_ID" \
  --region "$AWS_REGION" > /dev/null 2>&1 || true

aws lambda add-permission \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --statement-id "$STATEMENT_ID" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$AWS_REGION:$ACCOUNT_ID:$API_ID/*/*/*" \
  --region "$AWS_REGION" > /dev/null

echo "Lambda invoke permission added."

API_ENDPOINT="$(aws apigatewayv2 get-api \
  --api-id "$API_ID" \
  --region "$AWS_REGION" \
  --query "ApiEndpoint" \
  --output text)"

echo ""
echo "Step 9: Testing API Gateway health endpoint..."

sleep 5

if curl -fsS "$API_ENDPOINT/health" > /tmp/cloud-music-api-health.json; then
  echo "API Gateway health check passed."
  cat /tmp/cloud-music-api-health.json
  echo ""
else
  echo "WARNING: API Gateway health endpoint did not respond successfully yet."
  echo "Try manually:"
  echo "curl -v $API_ENDPOINT/health"
fi

echo ""
echo "========================================================="
echo "API Gateway deployment complete."
echo "API name:"
echo "$API_GATEWAY_NAME"
echo ""
echo "API ID:"
echo "$API_ID"
echo ""
echo "API endpoint:"
echo "$API_ENDPOINT"
echo ""
echo "Health check:"
echo "$API_ENDPOINT/health"
echo ""
echo "Example login test:"
echo "curl -X POST $API_ENDPOINT/login -H 'Content-Type: application/json' -d '{\"email\":\"s40978850@student.rmit.edu.au\",\"password\":\"012345\"}'"
echo "========================================================="