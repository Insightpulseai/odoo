#!/bin/bash
set -e

ENV=$1
PREVIOUS_TAG=$2

if [[ -z "$ENV" || -z "$PREVIOUS_TAG" ]]; then
  echo "Usage: ./rollback.sh <env> <previous_tag>"
  exit 1
fi

echo "⏪ Rolling back $ENV to $PREVIOUS_TAG..."

# Update RELEASE_TAG for the environment
export RELEASE_TAG=$PREVIOUS_TAG

# Re-deploy with previous tag
./scripts/deploy/deploy.sh $ENV $PREVIOUS_TAG

echo "✅ Rollback to $PREVIOUS_TAG successful!"
