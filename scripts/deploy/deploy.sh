#!/bin/bash
set -e

ENV=$1
TAG=${2:-latest}

if [[ -z "$ENV" ]]; then
  echo "Usage: ./deploy.sh <env> [tag]"
  exit 1
fi

echo "🚀 Deploying to $ENV with tag $TAG..."

# Load environment-specific variables
if [[ -f ".env.$ENV" ]]; then
  export $(cat .env.$ENV | xargs)
fi

# Pull latest image
echo "📥 Pulling image..."
docker compose -f docker/compose/$ENV.yml pull

# Start services
echo "⚡ Starting services..."
docker compose -f docker/compose/$ENV.yml up -d

# Run healthcheck
echo "🏥 Running healthcheck..."
./scripts/deploy/healthcheck.sh $ENV

echo "✅ Deployment to $ENV successful!"
