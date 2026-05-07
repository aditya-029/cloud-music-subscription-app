#!/bin/bash

set -e

# =========================================================
# Deploy Flask Backend to ECS Fargate
# Run from project root:
#   ./scripts/deploy_backend_ecs.sh
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/config.sh"

cd "$PROJECT_ROOT"

echo "========================================================="
echo "Cloud Music Backend - ECS Deployment"
echo "========================================================="

echo ""
echo "Step 1: Checking AWS credentials..."
aws sts get-caller-identity > /dev/null
echo "AWS credentials are valid."

echo ""
echo "Step 2: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
  echo "ERROR: Docker is not running."
  echo "Start Docker Desktop and rerun this script."
  exit 1
fi
echo "Docker is running."

echo ""
echo "Step 3: Getting AWS account ID and LabRole ARN..."
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
LAB_ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$LAB_ROLE_NAME"

echo "Account ID: $ACCOUNT_ID"
echo "LabRole ARN: $LAB_ROLE_ARN"

ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"

echo ""
echo "Step 4: Creating ECR repository if needed..."

if aws ecr describe-repositories \
  --repository-names "$ECR_REPOSITORY_NAME" \
  --region "$AWS_REGION" > /dev/null 2>&1; then
  echo "ECR repository already exists: $ECR_REPOSITORY_NAME"
else
  aws ecr create-repository \
    --repository-name "$ECR_REPOSITORY_NAME" \
    --region "$AWS_REGION" > /dev/null

  echo "Created ECR repository: $ECR_REPOSITORY_NAME"
fi

echo ""
echo "Step 5: Logging Docker into ECR..."

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo ""
echo "Step 6: Building Docker image..."

docker build \
  -f deployments/ecs/Dockerfile \
  -t "$ECR_REPOSITORY_NAME:latest" \
  .

echo ""
echo "Step 7: Tagging and pushing image to ECR..."

docker tag "$ECR_REPOSITORY_NAME:latest" "$ECR_URI:latest"
docker push "$ECR_URI:latest"

echo ""
echo "Step 8: Creating ECS cluster if needed..."

if aws ecs describe-clusters \
  --clusters "$ECS_CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --query "clusters[0].status" \
  --output text 2>/dev/null | grep -q "ACTIVE"; then
  echo "ECS cluster already exists: $ECS_CLUSTER_NAME"
else
  aws ecs create-cluster \
    --cluster-name "$ECS_CLUSTER_NAME" \
    --region "$AWS_REGION" > /dev/null

  echo "Created ECS cluster: $ECS_CLUSTER_NAME"
fi

echo ""
echo "Step 9: Finding default VPC and public subnets..."

VPC_ID="$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --region "$AWS_REGION" \
  --query "Vpcs[0].VpcId" \
  --output text)"

if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
  echo "ERROR: Could not find default VPC."
  exit 1
fi

SUBNET_IDS="$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=default-for-az,Values=true" \
  --region "$AWS_REGION" \
  --query "Subnets[*].SubnetId" \
  --output text)"

if [ -z "$SUBNET_IDS" ]; then
  echo "ERROR: Could not find default subnets."
  exit 1
fi

SUBNET_CSV="$(echo "$SUBNET_IDS" | tr '\t' ',' | tr ' ' ',')"

echo "Default VPC: $VPC_ID"
echo "Subnets: $SUBNET_CSV"

echo ""
echo "Step 10: Creating ECS security group if needed..."

SG_NAME="cloud-music-ecs-sg"

SECURITY_GROUP_ID="$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --region "$AWS_REGION" \
  --query "SecurityGroups[0].GroupId" \
  --output text 2>/dev/null || true)"

if [ "$SECURITY_GROUP_ID" = "None" ] || [ -z "$SECURITY_GROUP_ID" ]; then
  SECURITY_GROUP_ID="$(aws ec2 create-security-group \
    --group-name "$SG_NAME" \
    --description "Security group for Cloud Music ECS backend" \
    --vpc-id "$VPC_ID" \
    --region "$AWS_REGION" \
    --query "GroupId" \
    --output text)"

  echo "Created security group: $SECURITY_GROUP_ID"

  aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" > /dev/null

  echo "Added inbound HTTP port 80 rule."
else
  echo "Security group already exists: $SECURITY_GROUP_ID"
fi

echo ""
echo "Step 11: Registering ECS task definition..."

cat > /tmp/cloud-music-task-definition.json <<EOF
{
  "family": "$ECS_TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "taskRoleArn": "$LAB_ROLE_ARN",
  "executionRoleArn": "$LAB_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "$ECS_CONTAINER_NAME",
      "image": "$ECR_URI:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "AWS_REGION", "value": "$AWS_REGION" },
        { "name": "LOGIN_TABLE", "value": "$LOGIN_TABLE" },
        { "name": "MUSIC_TABLE", "value": "$MUSIC_TABLE" },
        { "name": "SUBSCRIPTIONS_TABLE", "value": "$SUBSCRIPTIONS_TABLE" },
        { "name": "MUSIC_TITLE_INDEX", "value": "$MUSIC_TITLE_INDEX" },
        { "name": "MUSIC_YEAR_ALBUM_INDEX", "value": "$MUSIC_YEAR_ALBUM_INDEX" },
        { "name": "APP_HOST", "value": "0.0.0.0" },
        { "name": "APP_PORT", "value": "80" },
        { "name": "FLASK_DEBUG", "value": "False" },
        { "name": "CORS_ORIGINS", "value": "*" },
        { "name": "S3_BUCKET_NAME", "value": "$ARTIST_IMAGE_BUCKET" },
        { "name": "S3_IMAGE_PREFIX", "value": "$S3_IMAGE_PREFIX" }
      ]
    }
  ]
}
EOF

TASK_DEFINITION_ARN="$(aws ecs register-task-definition \
  --cli-input-json file:///tmp/cloud-music-task-definition.json \
  --region "$AWS_REGION" \
  --query "taskDefinition.taskDefinitionArn" \
  --output text)"

echo "Registered task definition:"
echo "$TASK_DEFINITION_ARN"

echo ""
echo "Step 12: Creating or updating ECS service..."

SERVICE_EXISTS="$(aws ecs describe-services \
  --cluster "$ECS_CLUSTER_NAME" \
  --services "$ECS_SERVICE_NAME" \
  --region "$AWS_REGION" \
  --query "services[0].status" \
  --output text 2>/dev/null || true)"

NETWORK_CONFIGURATION="awsvpcConfiguration={subnets=[$SUBNET_CSV],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"

if [ "$SERVICE_EXISTS" = "ACTIVE" ]; then
  echo "ECS service already exists. Updating service..."

  aws ecs update-service \
    --cluster "$ECS_CLUSTER_NAME" \
    --service "$ECS_SERVICE_NAME" \
    --task-definition "$TASK_DEFINITION_ARN" \
    --desired-count 1 \
    --force-new-deployment \
    --region "$AWS_REGION" > /dev/null
else
  echo "Creating ECS service..."

  aws ecs create-service \
    --cluster "$ECS_CLUSTER_NAME" \
    --service-name "$ECS_SERVICE_NAME" \
    --task-definition "$TASK_DEFINITION_ARN" \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "$NETWORK_CONFIGURATION" \
    --region "$AWS_REGION" > /dev/null
fi

echo ""
echo "Step 13: Waiting for ECS service to become stable..."
aws ecs wait services-stable \
  --cluster "$ECS_CLUSTER_NAME" \
  --services "$ECS_SERVICE_NAME" \
  --region "$AWS_REGION"

echo "ECS service is stable."

echo ""
echo "Step 14: Finding running ECS task public IP..."

TASK_ARN="$(aws ecs list-tasks \
  --cluster "$ECS_CLUSTER_NAME" \
  --service-name "$ECS_SERVICE_NAME" \
  --desired-status RUNNING \
  --region "$AWS_REGION" \
  --query "taskArns[0]" \
  --output text)"

if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
  echo "ERROR: No running ECS task found."
  exit 1
fi

ENI_ID="$(aws ecs describe-tasks \
  --cluster "$ECS_CLUSTER_NAME" \
  --tasks "$TASK_ARN" \
  --region "$AWS_REGION" \
  --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" \
  --output text)"

PUBLIC_IP="$(aws ec2 describe-network-interfaces \
  --network-interface-ids "$ENI_ID" \
  --region "$AWS_REGION" \
  --query "NetworkInterfaces[0].Association.PublicIp" \
  --output text)"

echo ""
echo "========================================================="
echo "ECS backend deployment complete."
echo "ECR image:"
echo "$ECR_URI:latest"
echo ""
echo "ECS task public IP:"
echo "$PUBLIC_IP"
echo ""
echo "Health check:"
echo "http://$PUBLIC_IP/health"
echo "========================================================="