#!/bin/bash

# =========================================================
# Cloud Music Subscription App - Deployment Config
# Used by local AWS deployment scripts.
# =========================================================

# -----------------------------
# AWS / Lab Settings
# -----------------------------
export AWS_REGION="us-east-1"

# -----------------------------
# Project Names
# -----------------------------
export APP_NAME="cloud-music-subscription-app"
export PROJECT_ROOT_NAME="cloud-music-subscription-app"

# -----------------------------
# S3 Buckets
# -----------------------------
# Artist image bucket already used by backend/S3 image pipeline.
export ARTIST_IMAGE_BUCKET="cloud-music-app-s4097885-2026-a2"
export S3_IMAGE_PREFIX="artist-images/"

# Static React frontend hosting bucket.
# If this bucket name is taken globally, change only this value.
export FRONTEND_BUCKET="cloud-music-frontend-s4097885-2026-a2"

# -----------------------------
# DynamoDB Tables and Indexes
# -----------------------------
export LOGIN_TABLE="login"
export MUSIC_TABLE="music"
export SUBSCRIPTIONS_TABLE="subscriptions"

export MUSIC_TITLE_INDEX="title-index"
export MUSIC_YEAR_ALBUM_INDEX="year-album-index"

# -----------------------------
# Backend Runtime
# -----------------------------
export BACKEND_PORT="80"
export LOCAL_BACKEND_PORT="5050"

# -----------------------------
# ECS / ECR
# -----------------------------
export ECR_REPOSITORY_NAME="cloud-music-backend"
export ECS_CLUSTER_NAME="cloud-music-cluster"
export ECS_SERVICE_NAME="cloud-music-backend-service"
export ECS_TASK_FAMILY="cloud-music-backend-task"
export ECS_CONTAINER_NAME="cloud-music-backend"
export ECS_CONTAINER_PORT="80"

# -----------------------------
# Lambda / API Gateway
# -----------------------------
export LAMBDA_FUNCTION_NAME="cloud-music-backend-lambda"
export LAMBDA_PACKAGE_NAME="lambda_backend.zip"
export API_GATEWAY_NAME="cloud-music-api"

# -----------------------------
# Learner Lab IAM
# -----------------------------
# AWS Learner Lab provides these. Do not create new IAM roles.
export LAB_ROLE_NAME="LabRole"
export LAB_INSTANCE_PROFILE_NAME="LabInstanceProfile"

# -----------------------------
# Helper URLs
# -----------------------------
export FRONTEND_WEBSITE_URL="http://${FRONTEND_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"

echo_config() {
  echo "========================================================="
  echo "Cloud Music Deployment Config"
  echo "========================================================="
  echo "AWS_REGION:              $AWS_REGION"
  echo "FRONTEND_BUCKET:         $FRONTEND_BUCKET"
  echo "ARTIST_IMAGE_BUCKET:     $ARTIST_IMAGE_BUCKET"
  echo "LOGIN_TABLE:             $LOGIN_TABLE"
  echo "MUSIC_TABLE:             $MUSIC_TABLE"
  echo "SUBSCRIPTIONS_TABLE:     $SUBSCRIPTIONS_TABLE"
  echo "ECR_REPOSITORY_NAME:     $ECR_REPOSITORY_NAME"
  echo "ECS_CLUSTER_NAME:        $ECS_CLUSTER_NAME"
  echo "LAMBDA_FUNCTION_NAME:    $LAMBDA_FUNCTION_NAME"
  echo "FRONTEND_WEBSITE_URL:    $FRONTEND_WEBSITE_URL"
  echo "========================================================="
}