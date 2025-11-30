# AgriWeather IoT Platform - Azure Infrastructure Setup Script
# This script creates all necessary Azure resources for the platform
# Run from project root: .\scripts\setup_azure_infrastructure.ps1

$RESOURCE_GROUP = "rg-agriweather-iot"
$LOCATION = "francecentral"  # Change if needed
$IOT_HUB_NAME = "agriweather-hub-$(Get-Random -Minimum 1000 -Maximum 9999)"
$STORAGE_ACCOUNT_NAME = "agriweather$(Get-Random -Minimum 1000 -Maximum 9999)".ToLower()
$CONTAINER_NAME = "weather-data"
$VM_NAME = "agriweather-api-vm"
$VM_SIZE = "Standard_B1s"
$ADMIN_USERNAME = "azureuser"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AgriWeather IoT Platform Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "Checking Azure CLI installation..." -ForegroundColor Yellow
az version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Azure CLI is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host "Azure CLI found" -ForegroundColor Green
Write-Host ""

# Check if logged in
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
az account show | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
}
$subscription = az account show --query "{Name:name, Id:id}" -o json | ConvertFrom-Json
Write-Host "Using subscription: $($subscription.Name)" -ForegroundColor Green
Write-Host ""

# Create resource group
Write-Host "Creating resource group: $RESOURCE_GROUP" -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating resource group" -ForegroundColor Red
    exit 1
}
Write-Host "Resource group created" -ForegroundColor Green
Write-Host ""

# Create IoT Hub
Write-Host "Creating IoT Hub: $IOT_HUB_NAME" -ForegroundColor Yellow
az iot hub create `
    --resource-group $RESOURCE_GROUP `
    --name $IOT_HUB_NAME `
    --location $LOCATION `
    --sku F1 `
    --partition-count 2 `
    --retention-day 1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating IoT Hub" -ForegroundColor Red
    exit 1
}
Write-Host "IoT Hub created" -ForegroundColor Green
Write-Host ""

# Create storage account
Write-Host "Creating storage account: $STORAGE_ACCOUNT_NAME" -ForegroundColor Yellow
az storage account create `
    --resource-group $RESOURCE_GROUP `
    --name $STORAGE_ACCOUNT_NAME `
    --location $LOCATION `
    --sku Standard_LRS `
    --kind StorageV2 `
    --allow-blob-public-access false

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating storage account" -ForegroundColor Red
    exit 1
}
Write-Host "Storage account created" -ForegroundColor Green
Write-Host ""

# Get storage account key
Write-Host "Getting storage account key..." -ForegroundColor Yellow
$storageKey = az storage account keys list `
    --resource-group $RESOURCE_GROUP `
    --account-name $STORAGE_ACCOUNT_NAME `
    --query "[0].value" -o tsv

# Create blob container
Write-Host "Creating blob container: $CONTAINER_NAME" -ForegroundColor Yellow
az storage container create `
    --name $CONTAINER_NAME `
    --account-name $STORAGE_ACCOUNT_NAME `
    --account-key $storageKey `
    --public-access off

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating blob container" -ForegroundColor Red
    exit 1
}
Write-Host "Blob container created" -ForegroundColor Green
Write-Host ""

# Configure IoT Hub message routing to Blob Storage
Write-Host "Configuring IoT Hub message routing to Blob Storage..." -ForegroundColor Yellow
az iot hub routing-endpoint create `
    --resource-group $RESOURCE_GROUP `
    --hub-name $IOT_HUB_NAME `
    --endpoint-name storage-endpoint `
    --endpoint-type azurestoragecontainer `
    --endpoint-resource-group $RESOURCE_GROUP `
    --endpoint-subscription-id $subscription.Id `
    --connection-string "DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT_NAME;AccountKey=$storageKey;EndpointSuffix=core.windows.net" `
    --container-name $CONTAINER_NAME `
    --encoding json `
    --file-name-format "{iothub}/{partition}/{YYYY}/{MM}/{DD}/{HH}/{mm}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Message routing configured" -ForegroundColor Green
} else {
    Write-Host "Warning: Could not configure message routing (may need manual setup)" -ForegroundColor Yellow
}
Write-Host ""

# Create VM for REST API
Write-Host "Creating VM for REST API: $VM_NAME" -ForegroundColor Yellow
az vm create `
    --resource-group $RESOURCE_GROUP `
    --name $VM_NAME `
    --image Ubuntu2204 `
    --size $VM_SIZE `
    --admin-username $ADMIN_USERNAME `
    --generate-ssh-keys `
    --public-ip-sku Standard

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating VM" -ForegroundColor Red
    exit 1
}
Write-Host "VM created" -ForegroundColor Green
Write-Host ""

# Get VM public IP
Write-Host "Getting VM public IP..." -ForegroundColor Yellow
$vmIp = az vm show `
    --resource-group $RESOURCE_GROUP `
    --name $VM_NAME `
    --show-details `
    --query "publicIps" -o tsv

# Open HTTP port (5000 for Flask)
Write-Host "Configuring network security group for HTTP (port 5000)..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $RESOURCE_GROUP `
    --nsg-name "${VM_NAME}NSG" `
    --name allow-api-http `
    --protocol tcp `
    --priority 1000 `
    --destination-port-range 5000 `
    --access allow

Write-Host "Network security rule created" -ForegroundColor Green
Write-Host ""

# Create a device identity
Write-Host "Creating IoT device identity..." -ForegroundColor Yellow
$DEVICE_ID = "agriweather-device-001"
az iot hub device-identity create `
    --hub-name $IOT_HUB_NAME `
    --device-id $DEVICE_ID `
    --resource-group $RESOURCE_GROUP

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating device identity" -ForegroundColor Red
    exit 1
}
Write-Host "Device identity created: $DEVICE_ID" -ForegroundColor Green
Write-Host ""

# Get device connection string
Write-Host "Getting device connection string..." -ForegroundColor Yellow
$deviceConnStr = az iot hub device-identity connection-string show `
    --hub-name $IOT_HUB_NAME `
    --device-id $DEVICE_ID `
    --resource-group $RESOURCE_GROUP `
    --query "connectionString" -o tsv

# Get IoT Hub connection string (for backend)
$iotHubConnStr = az iot hub show-connection-string `
    --name $IOT_HUB_NAME `
    --resource-group $RESOURCE_GROUP `
    --query "connectionString" -o tsv

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Yellow
Write-Host "Location: $LOCATION" -ForegroundColor Yellow
Write-Host ""
Write-Host "IoT Hub Name: $IOT_HUB_NAME" -ForegroundColor Yellow
Write-Host "Storage Account: $STORAGE_ACCOUNT_NAME" -ForegroundColor Yellow
Write-Host "Container: $CONTAINER_NAME" -ForegroundColor Yellow
Write-Host "VM Name: $VM_NAME" -ForegroundColor Yellow
Write-Host "VM Public IP: $vmIp" -ForegroundColor Yellow
Write-Host "Device ID: $DEVICE_ID" -ForegroundColor Yellow
Write-Host ""
Write-Host "Device Connection String:" -ForegroundColor Cyan
Write-Host $deviceConnStr -ForegroundColor White
Write-Host ""
Write-Host "IoT Hub Connection String (for backend):" -ForegroundColor Cyan
Write-Host $iotHubConnStr -ForegroundColor White
Write-Host ""
Write-Host "Storage Account Key:" -ForegroundColor Cyan
Write-Host $storageKey -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "1. Set environment variable: `$env:IOT_HUB_CONNECTION_STRING='$deviceConnStr'" -ForegroundColor Yellow
Write-Host "2. Run device simulator: python device_simulator.py" -ForegroundColor Yellow
Write-Host "3. SSH to VM: ssh $ADMIN_USERNAME@$vmIp" -ForegroundColor Yellow
Write-Host "4. Deploy REST API to VM (see deployment instructions)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Save these connection strings securely!" -ForegroundColor Red
Write-Host ""

