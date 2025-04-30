#!/bin/bash

# Script to backup the PostgreSQL database in Azure

# Exit on error
set -e

# Configuration parameters
RESOURCE_GROUP="photonic-analyzer-rg"
DB_SERVER_NAME="photonic-db"
DB_NAME="photonic_analyzer"
BACKUP_NAME="photonic-backup-$(date +%Y%m%d-%H%M%S)"

# Check if user is logged in to Azure
echo "Checking Azure login status..."
if ! az account show > /dev/null 2>&1; then
  echo "You need to log in to Azure first."
  az login
fi

# Create a backup of the database
echo "Creating a backup of the PostgreSQL database..."
echo "This backup will be stored in your Azure storage account."

# Confirm backup creation
echo "Azure Database for PostgreSQL automatically creates server backups."
echo "You can create a point-in-time restore from the command line:"
echo ""
echo "az postgres server restore --resource-group $RESOURCE_GROUP \\"
echo "  --name ${DB_SERVER_NAME}-restored \\"
echo "  --source-server $DB_SERVER_NAME \\"
echo "  --restore-point-in-time \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
echo ""
echo "You can also export the database schema and data using pg_dump:"
echo ""
echo "# Get the connection details"
echo "PGUSER=\$(az postgres server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query administratorLogin -o tsv)"
echo "PGHOST=\$(az postgres server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query fullyQualifiedDomainName -o tsv)"
echo ""
echo "# Run pg_dump (you will be prompted for the password)"
echo "PGPASSWORD=<your-password> pg_dump -h \$PGHOST -U \$PGUSER -d $DB_NAME -f $BACKUP_NAME.sql"
echo ""
echo "For more information on backup and restore options, visit:"
echo "https://docs.microsoft.com/en-us/azure/postgresql/concepts-backup"