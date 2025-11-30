# AgriWeather IoT Platform - Azure Infrastructure Teardown Script
# This script removes all Azure resources created for the platform

param(
    [string]$ResourceGroup = "rg-agriweather-iot"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AgriWeather IoT Platform - Teardown" -ForegroundColor Cyan
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

# Check if resource group exists
Write-Host "Checking if resource group exists: $ResourceGroup" -ForegroundColor Yellow
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "false") {
    Write-Host "Resource group $ResourceGroup does not exist. Nothing to delete." -ForegroundColor Yellow
    exit 0
}
Write-Host "Resource group found" -ForegroundColor Green
Write-Host ""

# List resources in the resource group
Write-Host "Resources in resource group:" -ForegroundColor Yellow
az resource list --resource-group $ResourceGroup --output table
Write-Host ""

# Confirm deletion
Write-Host "WARNING: This will delete ALL resources in the resource group: $ResourceGroup" -ForegroundColor Red
$confirm = Read-Host "Type 'yes' to confirm deletion"
if ($confirm -ne "yes") {
    Write-Host "Deletion cancelled." -ForegroundColor Yellow
    exit 0
}

# Delete resource group (this deletes all resources in it)
Write-Host ""
Write-Host "Deleting resource group and all resources..." -ForegroundColor Yellow
az group delete --name $ResourceGroup --yes --no-wait

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Teardown Initiated!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resource group deletion has been initiated." -ForegroundColor Yellow
Write-Host "This may take several minutes to complete." -ForegroundColor Yellow
Write-Host ""
Write-Host "To check deletion status:" -ForegroundColor Cyan
Write-Host "  az group show --name $ResourceGroup" -ForegroundColor White
Write-Host ""

