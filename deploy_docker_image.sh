#!/bin/bash

# Exit on error
set -e

# Default to beta deployment
DEPLOY_ENV="beta"
AWS_PROFILE="instapod-beta"
ECR_REPO="134051051791.dkr.ecr.us-east-1.amazonaws.com"
REPO_NAME="podcast-generator-lambda-dev"
AWS_REGION="us-east-1"

# Check for --prod flag
if [[ "$1" == "--prod" ]]; then
    DEPLOY_ENV="prod"
    AWS_PROFILE="instapod-prod"
    ECR_REPO="450946881138.dkr.ecr.us-east-1.amazonaws.com"
    REPO_NAME="podcast-generator-lambda-prod"
    AWS_REGION="us-east-1"
    
    echo "⚠️  WARNING: You are deploying to PRODUCTION ⚠️"
    echo "This will affect live users. Are you sure you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
    echo "Proceeding with production deployment..."
fi

echo "Setting AWS profile to $AWS_PROFILE..."
export AWS_PROFILE=$AWS_PROFILE

#TODO: verify aws creds are set


echo "Logging into AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

echo "Building Docker image..."
docker build -t $REPO_NAME .

echo "Tagging Docker image..."
docker tag $REPO_NAME:latest $ECR_REPO/$REPO_NAME:latest

echo "Pushing Docker image to ECR..."
docker push $ECR_REPO/$REPO_NAME:latest

echo "Updating Lambda function to use the new image..."
aws lambda update-function-code --function-name instapod-podcast-generation --image-uri $ECR_REPO/$REPO_NAME:latest --region $AWS_REGION

echo "Deployment to $DEPLOY_ENV completed successfully!"