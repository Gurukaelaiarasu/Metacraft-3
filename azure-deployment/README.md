# Deploying to Azure

This directory contains the configuration files necessary to deploy the Deep Learning-Based Photonic & Plasmonic Structure Analyzer to Azure.

## Prerequisites

1. An Azure account with active subscription
2. Azure CLI installed and configured
3. Docker installed locally (for testing)
4. PostgreSQL database instance (Azure Database for PostgreSQL or similar)

## Deployment Steps

### 1. Create Azure Resources

You'll need:
- Azure Container Registry (ACR) to store your Docker images
- Azure App Service to host the application
- Azure Database for PostgreSQL for database storage

```bash
# Log in to Azure
az login

# Create a resource group
az group create --name photonic-analyzer-rg --location eastus

# Create Container Registry
az acr create --resource-group photonic-analyzer-rg \
  --name photonicanalyzeracr --sku Basic

# Create Azure Database for PostgreSQL
az postgres server create \
  --resource-group photonic-analyzer-rg \
  --name photonic-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password <your-secure-password> \
  --sku-name GP_Gen5_2

# Create a PostgreSQL database
az postgres db create \
  --resource-group photonic-analyzer-rg \
  --server-name photonic-db \
  --name photonic_analyzer

# Create App Service Plan
az appservice plan create \
  --resource-group photonic-analyzer-rg \
  --name photonic-plan \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --resource-group photonic-analyzer-rg \
  --plan photonic-plan \
  --name photonic-analyzer \
  --deployment-container-image-name photonicanalyzeracr.azurecr.io/photonic-structure-analyzer:latest
```

### 2. Configure Environment Variables

Set the necessary environment variables for the application:

```bash
# Set the PostgreSQL connection string
az webapp config appsettings set \
  --resource-group photonic-analyzer-rg \
  --name photonic-analyzer \
  --settings \
  DATABASE_URL="postgresql://dbadmin:<your-password>@photonic-db.postgres.database.azure.com:5432/photonic_analyzer?sslmode=require" \
  PORT=8000
```

### 3. Connect Azure Container Registry to App Service

```bash
# Get the ACR registry username and password
ACR_USERNAME=$(az acr credential show \
  --name photonicanalyzeracr \
  --query "username" -o tsv)
  
ACR_PASSWORD=$(az acr credential show \
  --name photonicanalyzeracr \
  --query "passwords[0].value" -o tsv)

# Configure the web app to use container registry
az webapp config container set \
  --name photonic-analyzer \
  --resource-group photonic-analyzer-rg \
  --docker-custom-image-name photonicanalyzeracr.azurecr.io/photonic-structure-analyzer:latest \
  --docker-registry-server-url https://photonicanalyzeracr.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD
```

### 4. Deploy Using Azure Pipelines

To use Azure DevOps for CI/CD:

1. Create a new Azure DevOps project
2. Import the repository with this code
3. Create a new pipeline using the `azure-pipelines.yml` file in this directory
4. Update the variables in the pipeline file to match your environment
5. Run the pipeline to build and deploy the application

## Testing Locally

You can test the Docker container locally before deploying:

```bash
# Build the image
docker build -t photonic-analyzer -f azure-deployment/Dockerfile .

# Run the container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:port/database" \
  photonic-analyzer
```

Then open http://localhost:8000 in your browser.

## Additional Configuration

The `config.toml` file contains Streamlit-specific configurations. Modify this file to adjust Streamlit behavior if needed.