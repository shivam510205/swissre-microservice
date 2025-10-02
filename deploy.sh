#!/bin/bash

set -e

ENVIRONMENT=${1:-dev}
NAMESPACE="is-mlops"
CHART_PATH="./helm"

echo "🚀 Deploying SwissRe to $ENVIRONMENT environment..."

# Deploy with Helm
RELEASE_NAME="swissre-$ENVIRONMENT"

helm upgrade --install $RELEASE_NAME $CHART_PATH \
    --namespace $NAMESPACE \
    --values $CHART_PATH/values-$ENVIRONMENT.yaml \
    --wait \
    --timeout 10m

echo "✅ SwissRe deployment complete!"

# Show status
kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=swissre-microservice
kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=swissre-microservice

echo ""
echo "🔗 Access:"
echo "Frontend: kubectl port-forward svc/swissre-$ENVIRONMENT-frontend 8501:8501 -n $NAMESPACE"
echo "Backend: kubectl port-forward svc/swissre-$ENVIRONMENT-backend 8080:8080 -n $NAMESPACE"
