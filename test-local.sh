#!/bin/bash

echo "🧪 Testing SwissRe Microservice Locally..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Build images locally
echo "🐳 Building Docker images..."
docker build -f docker/Dockerfile.backend -t swissre-api:local .
docker build -f docker/Dockerfile.frontend -t swissre-streamlit:local .

# Create network
echo "🌐 Creating Docker network..."
docker network create swissre-network 2>/dev/null || true

# Run backend
echo "🚀 Starting backend..."
docker run -d --name swissre-backend \
    --network swissre-network \
    -p 8080:8080 \
    -e AWS_REGION=us-east-1 \
    -e SWISSRE_SECRET_NAME=swissre/api-token \
    -e LOG_LEVEL=DEBUG \
    swissre-api:local

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Run frontend
echo "🎨 Starting frontend..."
docker run -d --name swissre-frontend \
    --network swissre-network \
    -p 8501:8501 \
    -e SWISSRE_API_URL=http://swissre-backend:8080 \
    swissre-streamlit:local

echo "✅ SwissRe microservice started locally!"
echo ""
echo "🔗 Access URLs:"
echo "   Backend API: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo "   Streamlit UI: http://localhost:8501"
echo ""
echo "📊 Container Status:"
docker ps --filter name=swissre

echo ""
echo "🛑 To stop: docker stop swissre-backend swissre-frontend && docker rm swissre-backend swissre-frontend"
