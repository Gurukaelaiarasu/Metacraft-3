#!/bin/bash

# Script to build and deploy the application to Azure

# Exit on error
set -e

# Configuration parameters
RESOURCE_GROUP="photonic-analyzer-rg"
ACR_NAME="photonicanalyzeracr"
APP_NAME="photonic-analyzer"
IMAGE_NAME="photonic-structure-analyzer"
TAG="latest"

# Check if user is logged in to Azure
echo "Checking Azure login status..."
if ! az account show > /dev/null 2>&1; then
  echo "You need to log in to Azure first."
  az login
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG -f azure-deployment/Dockerfile .

# Login to Azure Container Registry
echo "Logging in to Azure Container Registry..."
az acr login --name $ACR_NAME

# Push the image to ACR
echo "Pushing image to Azure Container Registry..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Deploy the application using ARM template
echo "Deploying application to Azure..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azure-deployment/app_service/template.json \
  --parameters @azure-deployment/app_service/parameters.json

# Get the application URL
WEB_APP_URL=$(az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query "defaultHostName" -o tsv)

echo "Deployment completed successfully!"
echo "Your application is now available at: https://$WEB_APP_URL"