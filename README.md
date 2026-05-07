# Project Overview

Cloud Music Subscription App is an AWS-based online music subscription
web application developed for Cloud Computing Assignment 2. The app
allows users to register, log in, search for songs, subscribe to songs,
remove subscriptions, and view artist images stored in Amazon S3.

The project demonstrates the same application deployed using multiple
AWS backend architectures:

- Frontend hosted using Amazon S3 static website hosting

- Backend deployed on EC2

- Backend deployed on ECS/Fargate

- Backend deployed using API Gateway and Lambda

- Application data stored in DynamoDB

- Artist images stored in S3

For the final demo, the frontend can be connected to any deployed
backend by rebuilding it with the required backend URL.

# Technology Stack

## Frontend

- React JS

- Vite

- Axios

- Tailwind CSS

- Amazon S3 static website hosting

## Backend

- Python

- Flask

- Gunicorn

- Boto3

- Native AWS Lambda router

## AWS Services

- Amazon DynamoDB

- Amazon S3

- Amazon EC2

- Amazon ECS/Fargate

- Amazon ECR

- AWS Lambda

- Amazon API Gateway

- Amazon CloudWatch

# Project Structure

```{style="textstyle"}
cloud-music-subscription-app/
|
|-- backend/
|   |-- app.py
|   |-- config.py
|   |-- routes/
|   |-- services/
|   |-- utils/
|
|-- data/
|   |-- 2026a2_songs.json
|
|-- database/
|   |-- analyse_dataset.py
|   |-- create_login_table.py
|   |-- create_music_table.py
|   |-- create_subscriptions_table.py
|   |-- import_login_users.py
|   |-- import_music_data.py
|   |-- verify_database.py
|   |-- db_config.py
|
|-- deployments/
|   |-- ec2/
|   |   |-- setup_ec2.sh
|   |   |-- run_backend.sh
|   |-- ecs/
|   |   |-- Dockerfile
|   |-- lambda/
|       |-- lambda_function.py
|
|-- docs/
|
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- package.json
|   |-- vite.config.js
|
|-- s3/
|   |-- upload_artist_images.py
|
|-- scripts/
|   |-- config.sh
|   |-- deploy_frontend_s3.sh
|   |-- deploy_backend_ecs.sh
|   |-- package_lambda.sh
|   |-- deploy_lambda.sh
|   |-- deploy_api_gateway.sh
|
|-- requirements.txt
|-- env.example
|-- .gitignore
|-- .dockerignore
|-- README.md
```

# How the Application Works

The React frontend provides the user interface for login, registration,
music search, subscriptions, and logout.

The backend provides API endpoints for authentication, music retrieval,
subscription management, and artist image URL generation.

DynamoDB stores users, music records, and subscriptions. S3 stores
artist images. The backend generates image URLs and returns them to the
frontend so artist images can be displayed in the app.

The same core backend logic is deployed in three ways:

1.  EC2 backend using Flask and Gunicorn

2.  ECS/Fargate backend using a Docker container

3.  API Gateway and Lambda backend using a native Lambda router

# AWS Credentials Setup

Before running any AWS setup or deployment scripts, configure AWS
Academy credentials locally.

Update the following file:

    ~/.aws/credentials

Example format:

    [default]
    aws_access_key_id=YOUR_ACCESS_KEY
    aws_secret_access_key=YOUR_SECRET_KEY
    aws_session_token=YOUR_SESSION_TOKEN

Set the AWS region and disable CLI paging:

    aws configure set region us-east-1
    aws configure set output json
    aws configure set cli_pager ""
    export AWS_PAGER=""

Check AWS access:

    aws sts get-caller-identity

Check DynamoDB access:

    aws dynamodb list-tables --region us-east-1

If an `ExpiredTokenException` occurs, refresh the AWS Academy Learner
Lab credentials and update `~/.aws/credentials`.

# Local Backend Environment Setup

Install Python dependencies:

    pip install -r requirements.txt

Create a local `.env` file:

    cp env.example .env

Example `.env` values:

    AWS_REGION=us-east-1
    LOGIN_TABLE=login
    MUSIC_TABLE=music
    SUBSCRIPTIONS_TABLE=subscriptions
    MUSIC_TITLE_INDEX=title-index
    MUSIC_YEAR_ALBUM_INDEX=year-album-index
    APP_HOST=0.0.0.0
    APP_PORT=5050
    FLASK_DEBUG=True
    CORS_ORIGINS=*
    S3_BUCKET_NAME=cloud-music-app-s4097885-2026-a2
    S3_IMAGE_PREFIX=artist-images/

Do not commit `.env`.

# DynamoDB Setup

Run these commands from the project root.

Analyse the dataset:

    python -m database.analyse_dataset

Create DynamoDB tables:

    python -m database.create_login_table
    python -m database.create_music_table
    python -m database.create_subscriptions_table

Import default login users:

    python -m database.import_login_users

Import music records:

    python -m database.import_music_data

Verify the database setup:

    python -m database.verify_database

The verification script checks the login, music, and subscriptions
tables. It also confirms that the GSI, LSI, Query, and controlled Scan
operations are working.

# S3 Artist Image Setup

Upload artist images to S3 and update DynamoDB records:

    python -m s3.upload_artist_images

This uploads artist images under:

    artist-images/

in the artist image bucket and updates music records with
`s3_image_key`.

# Run Backend Locally

Start the Flask backend:

    APP_PORT=5050 python -m backend.app

Test health:

    curl http://127.0.0.1:5050/health

Test login:

    curl -X POST http://127.0.0.1:5050/login \
      -H "Content-Type: application/json" \
      -d '{"email":"s40978850@student.rmit.edu.au","password":"012345"}'

Test music search:

    curl "http://127.0.0.1:5050/songs?artist=Taylor%20Swift&album=Fearless"

# Run Frontend Locally

Go to the frontend folder:

    cd frontend
    npm install

Create a frontend `.env` file if required:

    cp .env.example .env

For local backend testing, set:

    VITE_API_BASE_URL=http://127.0.0.1:5050

Run the frontend:

    npm run dev

Open the local Vite URL printed in the terminal.

# Deploy Frontend to S3

From the project root:

    ./scripts/deploy_frontend_s3.sh

To deploy the frontend against a specific backend URL:

    VITE_API_BASE_URL=http://BACKEND_URL ./scripts/deploy_frontend_s3.sh

For API Gateway backend:

    VITE_API_BASE_URL=https://API_GATEWAY_URL ./scripts/deploy_frontend_s3.sh

Frontend S3 website URL:

    http://cloud-music-frontend-s4097885-2026-a2.s3-website-us-east-1.amazonaws.com

For demo testing, open the S3 website, log in, search songs, subscribe,
remove a subscription, and logout.

# Deploy Backend on EC2

## EC2 Console Setup

Launch an EC2 instance with:

- Region: `us-east-1`

- AMI: Amazon Linux 2023

- Instance type: `t2.micro` or `t3.micro`

- Key pair: `vockey`

- IAM instance profile: `LabInstanceProfile`

- Inbound rule: HTTP TCP 80 from `0.0.0.0/0`

- Inbound rule: SSH TCP 22 from My IP

SSH into EC2:

    ssh -i labsuser.pem ec2-user@EC2_PUBLIC_IP

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/cloud-music-subscription-app.git
    cd cloud-music-subscription-app

Run EC2 setup:

    chmod +x deployments/ec2/setup_ec2.sh
    ./deployments/ec2/setup_ec2.sh

Start the EC2 backend:

    chmod +x deployments/ec2/run_backend.sh
    ./deployments/ec2/run_backend.sh

Test from your local machine:

    curl http://EC2_PUBLIC_IP/health

To connect the S3 frontend to EC2:

    VITE_API_BASE_URL=http://EC2_PUBLIC_IP ./scripts/deploy_frontend_s3.sh

# Deploy Backend on ECS/Fargate

Make sure Docker Desktop is running.

From the project root:

    ./scripts/deploy_backend_ecs.sh

The script will:

- Build the backend Docker image

- Push it to Amazon ECR

- Create or update the ECS cluster

- Register a Fargate task definition

- Create or update the ECS service

- Print the ECS task public IP

Test the ECS backend:

    curl http://ECS_PUBLIC_IP/health

To connect the S3 frontend to ECS:

    VITE_API_BASE_URL=http://ECS_PUBLIC_IP ./scripts/deploy_frontend_s3.sh

# Deploy Backend Using Lambda and API Gateway

Deploy Lambda:

    ./scripts/deploy_lambda.sh

Deploy API Gateway:

    ./scripts/deploy_api_gateway.sh

The API Gateway script prints the API endpoint.

Test API Gateway health:

    curl https://API_GATEWAY_URL/health

Test login:

    curl -X POST https://API_GATEWAY_URL/login \
      -H "Content-Type: application/json" \
      -d '{"email":"s40978850@student.rmit.edu.au","password":"012345"}'

Test search:

    curl "https://API_GATEWAY_URL/songs?artist=Taylor%20Swift&album=Fearless"

Test subscriptions:

    curl "https://API_GATEWAY_URL/subscriptions?email=s40978850@student.rmit.edu.au"

To connect the S3 frontend to API Gateway:

    VITE_API_BASE_URL=https://API_GATEWAY_URL ./scripts/deploy_frontend_s3.sh

# Backend API Routes

The backend supports:

    GET    /health
    POST   /login
    POST   /register
    GET    /songs
    GET    /subscriptions
    POST   /subscriptions
    DELETE /subscriptions/<email>/<song_id>

Example song search:

    curl "https://API_GATEWAY_URL/songs?artist=Taylor%20Swift&album=Fearless"

Example subscriptions request:

    curl "https://API_GATEWAY_URL/subscriptions?email=s40978850@student.rmit.edu.au"

# Demo Checklist

Before the demo, verify:

1.  AWS credentials are active.

2.  DynamoDB tables exist: `login`, `music`, `subscriptions`.

3.  S3 artist image bucket exists.

4.  S3 frontend URL loads.

5.  EC2 backend `/health` works.

6.  ECS backend `/health` works.

7.  API Gateway `/health` works.

8.  Frontend is deployed using the backend URL selected for the demo.

9.  Login works from the frontend.

10. Search returns songs with artist images.

11. Subscribe adds a song.

12. Remove deletes a subscription.

13. Logout returns to the login page.

Recommended final demo backend:

    API Gateway + Lambda

This clearly demonstrates the serverless deployment requirement.

# Useful Demo Search Values

Use these values during the demo:

    Artist: Taylor Swift
    Album: Fearless

    Artist: Jimmy Buffett
    Year: 1974

    Title: Bad Blood
    Artist: Taylor Swift

# Git and Security Notes

Do not commit:

- `.env`

- `frontend/.env`

- `frontend/node_modules/`

- `frontend/dist/`

- `lambda_build/`

- `lambda_backend.zip`

- `tmp_artist_images/`

- `__pycache__/`

- `.DS_Store`

- `*.pem`

- AWS credentials

Commit:

- `README.md`

- `requirements.txt`

- `env.example`

- `.gitignore`

- `.dockerignore`

- `backend/`

- `database/`

- `data/`

- `s3/`

- `frontend/src/`

- `deployments/`

- `scripts/`

- `docs/`

# Cost-Safe AWS Usage

To avoid unnecessary AWS Academy credit usage:

- Stop EC2 after testing.

- Delete or scale down ECS service if not needed.

- Do not create large EC2 instances.

- Do not leave compute resources running overnight.

- Refresh AWS Academy credentials when `ExpiredTokenException` occurs.

- Use `us-east-1` consistently.

Stop EC2 from the AWS Console when not testing:

    EC2 -> Instances -> select instance -> Instance state -> Stop instance

Scale down ECS if needed:

    aws ecs update-service \
      --cluster cloud-music-cluster \
      --service cloud-music-backend-service \
      --desired-count 0 \
      --region us-east-1

Restore ECS later:

    aws ecs update-service \
      --cluster cloud-music-cluster \
      --service cloud-music-backend-service \
      --desired-count 1 \
      --region us-east-1

# Final Submission Cleanup

Before creating the final submission zip, check for unwanted files:

    find . -name "__pycache__" -type d
    find . -name ".DS_Store" -type f
    find . -name "node_modules" -type d
    find . -name ".env" -type f
    find . -name "lambda_backend.zip" -type f
    find . -name "lambda_build" -type d

Remove unwanted files before zipping.

The final submission should include source code, deployment scripts,
report PDF, and group worklog PDF.

# Create README File from Terminal

Run this from your project root:

    cat > README.md <<'EOF'
    # Cloud Music Subscription App

    Paste the final README Markdown content here.

    EOF

Then check it rendered properly:

    cat README.md

Commit it:

    git add README.md
    git commit -m "Update README for final deployment demo"
    git push
