#!/bin/bash

# Set env vars
echo "export ALPACA_API_KEY=${alpaca_api_key}" >> /etc/environment
echo "export ALPACA_API_SECRET=${alpaca_api_secret}" >> /etc/environment
echo "export QDRANT_API_KEY=${qdrant_api_key}" >> /etc/environment
echo "export QDRANT_URL=${qdrant_url}" >> /etc/environment

# Install Docker
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install AWS CLI
sudo yum install -y aws-cli

# Authenticate Docker to the ECR registry
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${ecr_repository_url}

# Pull Docker image from ECR
docker pull ${ecr_repository_url}:latest

# Run Docker image
source /etc/environment && docker run -d \
    -e BYTEWAX_PYTHON_FILE_PATH=tools.run_real_time:build_flow \
    -e ALPACA_API_KEY=$${ALPACA_API_KEY} \
    -e ALPACA_API_SECRET=$${ALPACA_API_SECRET} \
    -e QDRANT_API_KEY=$${QDRANT_API_KEY} \
    -e QDRANT_URL=$${QDRANT_URL} \
    --name streaming_pipeline \
    ${ecr_repository_url}:latest