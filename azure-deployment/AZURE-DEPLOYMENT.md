# Azure Deployment Guide for Photonic & Plasmonic Structure Analyzer

This guide provides step-by-step instructions for deploying the Deep Learning-Based Photonic & Plasmonic Structure Analyzer application to Microsoft Azure.

## Prerequisites

- An Azure account with an active subscription
- Azure CLI installed locally
- Docker installed locally
- Git for cloning the repository

## Deployment Files

This deployment package includes the following files:

- `Dockerfile`: Container definition for the application
- `config.toml`: Streamlit configuration file
- `requirements.txt`: Python dependencies
- `.dockerignore`: Files to exclude from the Docker image
- `setup_infra.sh`: Script to set up initial Azure infrastructure
- `deploy.sh`: Script to build and deploy the application
- `local-test.sh`: Script to test the application locally
- `backup-database.sh`: Information about database backup options
- `app_service/`: ARM templates for Azure App Service deployment

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up Azure Infrastructure

Run the infrastructure setup script:

```bash
./azure-deployment/setup_infra.sh
```

This script will:
- Create a resource group
- Create an Azure Container Registry
- Create an Azure Database for PostgreSQL server and database
- Configure firewall rules for the database
- Create an App Service Plan
- Update deployment parameters

You will be prompted to provide a secure password for the database administrator account.

### 3. Test Locally (Optional)

Before deploying to Azure, you can test the application locally:

```bash
./azure-deployment/local-test.sh
```

This script will build the Docker image and run it locally, connecting to the database you specify. 

### 4. Deploy to Azure

Once you've confirmed everything works correctly, deploy to Azure:

```bash
./azure-deployment/deploy.sh
```

This script will:
- Build the Docker image
- Push the image to Azure Container Registry
- Deploy the web app using ARM templates
- Show the URL where your application is available

## Post-Deployment

### Accessing Your Application

After successful deployment, your application will be available at:
`https://photonic-analyzer.azurewebsites.net`

### Database Management

The PostgreSQL database is managed by Azure and automatically backed up. For manual backups or data export, see:

```bash
./azure-deployment/backup-database.sh
```

### Scaling

To scale your application:

```bash
# Scale up (increase resources per instance)
az appservice plan update --name photonic-plan --resource-group photonic-analyzer-rg --sku S1

# Scale out (add more instances)
az appservice plan update --name photonic-plan --resource-group photonic-analyzer-rg --number-of-workers 3
```

### Monitoring

Monitor your application's performance:

```bash
# View application logs
az webapp log tail --name photonic-analyzer --resource-group photonic-analyzer-rg

# Set up monitoring and alerts in Azure Portal
az monitor metrics alert create [...]
```

## Troubleshooting

### Common Issues

1. **Container fails to start**: Check the application logs in the Azure Portal or using Azure CLI:
   ```bash
   az webapp log tail --name photonic-analyzer --resource-group photonic-analyzer-rg
   ```

2. **Database connection issues**: Verify that the connection string is correctly set in the app settings:
   ```bash
   az webapp config appsettings list --name photonic-analyzer --resource-group photonic-analyzer-rg
   ```
   
3. **Poor performance**: Consider scaling up the App Service Plan or optimizing the application code.

### Getting Help

For issues with the application itself, refer to the application documentation or open an issue in the repository.

For Azure-specific issues, refer to the [Azure documentation](https://docs.microsoft.com/en-us/azure/) or contact Azure support.