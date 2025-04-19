#!/bin/bash

# Create deployment directory
mkdir -p deployment

# Copy Lambda function
cp lambda_function.py deployment/

# Install dependencies
pip install -r requirements.txt -t deployment/

# Create zip file
cd deployment
zip -r ../lambda_deployment.zip .

# Clean up
cd ..
rm -rf deployment

echo "Lambda deployment package created: lambda_deployment.zip" 