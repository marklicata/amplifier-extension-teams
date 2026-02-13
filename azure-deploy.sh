#!/bin/bash
# Deploy Amplifier Teams Bot to Azure Container Apps

set -e

# Set UTF-8 encoding for Azure CLI output on Windows
export PYTHONIOENCODING=utf-8

echo "🚀 Deploying Amplifier Teams Bot to Azure"
echo "=========================================="
echo ""

# Check required tools
command -v az >/dev/null 2>&1 || { echo "❌ Azure CLI not found. Install it first."; exit 1; }

# Load configuration
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-amplifier-rg}"
LOCATION="${LOCATION:-eastus}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-amplifier-teams-bot}"
CONTAINER_REGISTRY="${CONTAINER_REGISTRY:-acramplifieronboarding}"
IMAGE_NAME="${IMAGE_NAME:-amplifier-teams-bot}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Container App: $CONTAINER_APP_NAME"
echo "  Registry: $CONTAINER_REGISTRY"
echo ""

# Login to Azure
echo "Logging in to Azure..."
az account show >/dev/null 2>&1 || az login

echo "Setting Azure subscription..."
az account set --subscription "8a673afb-d858-4a97-a490-2625396d1484"


# Build and push image
echo "Skipping build - using existing image from registry..."
# Uncomment below to rebuild image (requires UTF-8 capable terminal)
# az acr build \
#     --registry "$CONTAINER_REGISTRY" \
#     --image "$IMAGE_NAME:$IMAGE_TAG" \
#     --file Dockerfile \
#     .

echo "Getting registry credentials..."
REGISTRY_SERVER=$(az acr show --name "$CONTAINER_REGISTRY" --query loginServer -o tsv | tr -d '\r\n')
REGISTRY_USERNAME=$(az acr credential show --name "$CONTAINER_REGISTRY" --query username -o tsv | tr -d '\r\n')
REGISTRY_PASSWORD=$(az acr credential show --name "$CONTAINER_REGISTRY" --query "passwords[0].value" -o tsv | tr -d '\r\n')

echo "Registry Server: $REGISTRY_SERVER"
echo "Image Reference: $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG"
echo ""

echo "Creating environment for Container App..."
# ENVIRONMENT_NAME="${CONTAINER_APP_NAME}-env"
# az containerapp env create \
#     --name "$ENVIRONMENT_NAME" \
#     --resource-group "$RESOURCE_GROUP" \
#     --location "$LOCATION"


# # Deploy container app
echo "Deploying container app..."
az containerapp update \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 4 \
    --memory 8Gi \
    --set-env-vars \
        "AMPLIFIER_API_URL=$AMPLIFIER_API_URL" \
        "AMPLIFIER_API_KEY=$AMPLIFIER_API_KEY" \
        "AMPLIFIER_BASE_CONFIG_ID=$AMPLIFIER_BASE_CONFIG_ID" \
        "AMPLIFIER_BASE_CONFIG_NAME=$AMPLIFIER_BASE_CONFIG_NAME" \
        "MICROSOFT_APP_ID=$MICROSOFT_APP_ID" \
        "MICROSOFT_APP_PASSWORD=secretref:teamsappapikey" \
        "PORT=3978" 

# # Get the app URL
APP_URL=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn \
    -o tsv)


# echo "Deploying Azure bot service..."
# az bot create \
#   --resource-group "$RESOURCE_GROUP" \
#   --name "$CONTAINER_APP_NAME" \
#   --kind registration \
#   --app-type MultiTenant \
#   --endpoint "https://$APP_URL/api/messages" \
#   --password "$REGISTRY_PASSWORD" \
#   --appid "$MICROSOFT_APP_ID"


# echo ""
echo "✅ Deployment complete!"
echo ""
echo "Bot Messaging Endpoint: https://$APP_URL/api/messages"
echo ""
echo "Bot name: $CONTAINER_APP_NAME"

echo "✅ Deployment complete! (Image pushed to ACR)"