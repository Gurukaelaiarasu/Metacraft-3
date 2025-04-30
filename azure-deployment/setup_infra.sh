#!/bin/bash

# Script to set up the initial Azure infrastructure for Photonic & Plasmonic Structure Analyzer

# Exit on error
set -e

# Configuration parameters
RESOURCE_GROUP="photonic-analyzer-rg"
LOCATION="eastus"
ACR_NAME="photonicanalyzeracr"
DB_SERVER_NAME="photonic-db"
DB_NAME="photonic_analyzer"
DB_ADMIN_USER="dbadmin"
APP_NAME="photonic-analyzer"
APP_PLAN="photonic-plan"

# Check if user is logged in to Azure
echo "Checking Azure login status..."
if ! az account show > /dev/null 2>&1; then
  echo "You need to log in to Azure first."
  az login
fi

# Create resource group
echo "Creating resource group '$RESOURCE_GROUP'..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating container registry '$ACR_NAME'..."
az acr create --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME --sku Basic

# Create PostgreSQL server
echo "Creating PostgreSQL server '$DB_SERVER_NAME'..."
echo "Please enter a secure password for the database admin user:"
read -s DB_ADMIN_PASSWORD
echo

az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user $DB_ADMIN_USER \
  --admin-password $DB_ADMIN_PASSWORD \
  --sku-name GP_Gen5_2

# Create PostgreSQL database
echo "Creating PostgreSQL database '$DB_NAME'..."
az postgres db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --name $DB_NAME

# Allow Azure services to access the server
echo "Configuring PostgreSQL firewall rules..."
az postgres server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --name "AllowAllAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Create App Service Plan
echo "Creating App Service Plan '$APP_PLAN'..."
az appservice plan create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_PLAN \
  --is-linux \
  --sku B1

# Update the parameters file with the database password
echo "Updating deployment parameters..."
# Replace empty password with the provided one (securely)
sed -i "s/\"databasePassword\": {\"value\": \"\"}/\"databasePassword\": {\"value\": \"$DB_ADMIN_PASSWORD\"}/" azure-deployment/app_service/parameters.json

echo "Infrastructure setup complete!"
echo ""
echo "Next steps:"
echo "1. Build and push your Docker image to the container registry"
echo "2. Deploy the application using the ARM template"
echo ""
echo "Example commands:"
echo "az acr login --name $ACR_NAME"
echo "docker build -t $ACR_NAME.azurecr.io/photonic-structure-analyzer:latest -f azure-deployment/Dockerfile ."
echo "docker push $ACR_NAME.azurecr.io/photonic-structure-analyzer:latest"
echo "az deployment group create --resource-group $RESOURCE_GROUP --template-file azure-deployment/app_service/template.json --parameters @azure-deployment/app_service/parameters.json"