#!/bin/bash

set -e

echo "🐳 Building SwissRe Docker Images..."

REGISTRY="securian-docker-all.jfrog.io"
BACKEND_IMAGE="$REGISTRY/swissre-api"
FRONTEND_IMAGE="$REGISTRY/swissre-streamlit"
TAG="dev-$(date +%Y%m%d-%H%M%S)"

echo "📦 Building Backend Image..."
docker build -f docker/Dockerfile.backend -t $BACKEND_IMAGE:$TAG -t $BACKEND_IMAGE:latest .

echo "📦 Building Frontend Image..."
docker build -f docker/Dockerfile.frontend -t $FRONTEND_IMAGE:$TAG -t $FRONTEND_IMAGE:latest .

echo "🚀 Pushing Images..."
docker push $BACKEND_IMAGE:$TAG
docker push $BACKEND_IMAGE:latest
docker push $FRONTEND_IMAGE:$TAG
docker push $FRONTEND_IMAGE:latest

echo "📝 Updating Helm values..."
sed -i.bak "s/tag: \".*\"/tag: \"$TAG\"/" helm/values-dev.yaml

echo "✅ Images ready: $TAG"
