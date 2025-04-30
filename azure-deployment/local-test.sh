#!/bin/bash

# Script to test the Docker container locally before deploying to Azure

# Exit on error
set -e

# Configuration parameters
IMAGE_NAME="photonic-analyzer"
PORT=8000

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Ask for local DB connection details
echo "Please enter your PostgreSQL database connection details for local testing:"
echo "Note: You can use a local PostgreSQL instance or Azure PostgreSQL with allowed IP."
echo

read -p "Database host: " DB_HOST
read -p "Database port (default 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}
read -p "Database name: " DB_NAME
read -p "Database user: " DB_USER
read -s -p "Database password: " DB_PASSWORD
echo

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME -f azure-deployment/Dockerfile .

# Run the container with the provided database connection
echo "Running container locally on port $PORT..."
docker run -p $PORT:$PORT \
  -e DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" \
  -e PORT=$PORT \
  $IMAGE_NAME

# Note: The above command will keep running until you press Ctrl+C