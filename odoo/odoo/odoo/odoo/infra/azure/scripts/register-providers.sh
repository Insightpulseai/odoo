#!/bin/bash
# infra/azure/scripts/register-providers.sh
# Registers essential Azure resource providers for the InsightPulseAI subscription.

set -e

SUBSCRIPTION_ID="536d8cf6-89e1-4815-aef3-d5f2c5f4d070"

echo "Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription "$SUBSCRIPTION_ID"

PROVIDERS=(
    "Microsoft.CloudShell"
    "Microsoft.Storage"
    "Microsoft.ContainerInstance"
    "Microsoft.Resources"
    "Microsoft.CognitiveServices"
    "Microsoft.Search"
    "Microsoft.Databricks"
)

for provider in "${PROVIDERS[@]}"; do
    echo "Registering $provider..."
    az provider register --namespace "$provider"
done

echo "Waiting for registration to complete (this may take a few minutes)..."
for provider in "${PROVIDERS[@]}"; do
    state=$(az provider show --namespace "$provider" --query registrationState -o tsv)
    echo "$provider: $state"
done
