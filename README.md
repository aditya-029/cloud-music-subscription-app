# Cloud Music Subscription App

## 1. Project Overview

This project is an AWS-based online music subscription web application developed for Cloud Computing Assignment 2. The application allows users to register, log in, search for music, subscribe to songs, remove subscriptions, and display artist images stored in Amazon S3.
The project currently includes the completed data layer, S3 image pipeline, and local Flask backend API. The remaining work includes frontend development and deployment across EC2, ECS, and API Gateway + Lambda.

## 2. Current Implementation Status

Completed so far:

- Analysed the `2026a2_songs.json` dataset.
- Created DynamoDB tables for users, music records, and subscriptions.
- Imported 10 default login users.
- Imported all 137 music records without overwriting duplicate song titles.
- Created a purposefully designed `music` table with one GSI and one LSI.
- Uploaded 71 unique artist images to Amazon S3.
- Updated DynamoDB music records with S3 image keys.
- Built a modular Flask backend API.
- Implemented login, register, music search, subscribe, remove, and health-check endpoints.
- Added presigned S3 image URLs for secure frontend image display.

## 3. Technology Stack

- Python
- Flask
- Boto3
- Amazon DynamoDB
- Amazon S3
- AWS CLI
- Python dotenv
- Gunicorn for later EC2/ECS deployment

## 4. Project Structure

```text
cloud-music-subscription-app/
│
├── data/
│   └── 2026a2_songs.json
│
├── database/
│   ├── analyse_dataset.py
│   ├── create_login_table.py
│   ├── create_music_table.py
│   ├── create_subscriptions_table.py
│   ├── db_config.py
│   ├── import_login_users.py
│   ├── import_music_data.py
│   └── verify_database.py
│
├── s3/
│   └── upload_artist_images.py
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── music_routes.py
│   │   └── subscription_routes.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── dynamodb_service.py
│   │   ├── music_service.py
│   │   ├── s3_service.py
│   │   └── subscription_service.py
│   └── utils/
│       └── response.py
│
├── deployments/
├── docs/
├── requirements.txt
├── env.example
├── .gitignore
└── README.md

5. Environment Setup

Install project dependencies:

pip install -r requirements.txt

Create the local environment file:

cp env.example .env

Example .env values:

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

Do not commit .env to GitHub.

6. AWS Credentials

AWS Academy credentials must be configured locally before running AWS-related scripts.

Check AWS access:

aws sts get-caller-identity

Check DynamoDB access:

aws dynamodb list-tables --region us-east-1

If an ExpiredTokenException occurs, refresh the AWS Academy CLI credentials and update ~/.aws/credentials.

7. DynamoDB Design

login table

Stores user login records.

Partition key: email

music table

Stores all music records from the dataset.

Partition key: artist
Sort key: title_year_album

Indexes:

GSI: title-index
LSI: year-album-index

This design prevents data loss because song titles are not unique in the dataset. The combination of title, artist, year, and album is used to generate a stable song_id.

subscriptions table

Stores user subscriptions.

Partition key: email
Sort key: song_id

8. Running the Data Setup

Run the following commands from the project root.

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

Verify database setup:

python -m database.verify_database

The verification script checks that:

* the login table exists,
* the music table contains 137 records,
* the subscriptions table exists,
* artist queries work,
* title-index GSI queries work,
* year-album LSI queries work,
* controlled scan operations work.

9. S3 Artist Image Setup

Upload artist images to S3 and update DynamoDB records:

python -m s3.upload_artist_images

This script:

* finds 71 unique artist image URLs,
* creates the S3 bucket if required,
* uploads images under artist-images/,
* updates each music record with its s3_image_key.

Test presigned image URL generation:

python - <<'PY'
from backend.services.s3_service import generate_presigned_image_url
print(generate_presigned_image_url("artist-images/TaylorSwift.jpg"))
PY

10. Running the Backend Locally

Start the Flask backend:

APP_PORT=5050 python -m backend.app

Test the health endpoint:

curl http://127.0.0.1:5050/health

Test login:

curl -X POST http://127.0.0.1:5050/login \
  -H "Content-Type: application/json" \
  -d '{"email":"s40978850@student.rmit.edu.au","password":"012345"}'

Test music search:

curl "http://127.0.0.1:5050/songs?artist=Taylor%20Swift&album=Fearless"

Test subscriptions:

curl "http://127.0.0.1:5050/subscriptions?email=s40978850@student.rmit.edu.au"

11. Current Backend API Routes

GET    /health
POST   /login
POST   /register
GET    /songs
GET    /subscriptions
POST   /subscriptions
DELETE /subscriptions/<email>/<song_id>

12. Git and Security Notes

Do not commit:

.env
tmp_artist_images/
virtual environments
__pycache__/
AWS credentials
temporary zip/build files

Commit:

README.md
requirements.txt
env.example
.gitignore
data/
database/
backend/
s3/
docs/
deployments/

13. Remaining Work

The remaining project tasks are:

1. Build frontend pages for login, registration, search, subscriptions, and logout.
2. Connect the frontend to the local Flask backend.
3. Deploy the frontend to S3 static hosting.
4. Deploy the backend independently on EC2.
5. Deploy the backend independently on ECS.
6. Deploy the backend using API Gateway + Lambda.
7. Prepare the final report, architecture diagrams, group worklog, and demo checklist.

```
