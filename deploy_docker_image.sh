#!/bin/bash

# Exit on error
set -e

# Default to beta deployment
DEPLOY_ENV="beta"
AWS_PROFILE="instapod-beta"
ECR_REPO="450946881138.dkr.ecr.us-east-2.amazonaws.com/instapod-podcast-generation-beta"

# Check for --prod flag
if [[ "$1" == "--prod" ]]; then
    # DEPLOY_ENV="prod"
    # AWS_PROFILE="instapod-prod"
    # ECR_REPO="450946881138.dkr.ecr.us-east-2.amazonaws.com/instapod-podcast-generation"
    
    # echo "⚠️  WARNING: You are deploying to PRODUCTION ⚠️"
    # echo "This will affect live users. Are you sure you want to continue? (y/N)"
    # read -r response
    # if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    #     echo "Deployment cancelled."
    #     exit 1
    # fi
    echo "Prod deployments not supported yet. All deployments use prod account currently"
        exit 1
fi

echo "Setting AWS profile to $AWS_PROFILE..."
export AWS_PROFILE=$AWS_PROFILE

echo "Logging into AWS ECR..."
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ECR_REPO

echo "Building Docker image..."
docker build -t instapod-podcast-generation .

echo "Tagging Docker image..."
docker tag instapod-podcast-generation:latest $ECR_REPO:latest

echo "Pushing Docker image to ECR..."
docker push $ECR_REPO:latest

echo "Deployment to $DEPLOY_ENV completed successfully!"