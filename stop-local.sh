#!/bin/bash

echo "🛑 Stopping SwissRe Microservice..."

# Stop containers
docker stop swissre-backend swissre-frontend 2>/dev/null || true

# Remove containers
docker rm swissre-backend swissre-frontend 2>/dev/null || true

# Remove network
docker network rm swissre-network 2>/dev/null || true

echo "✅ SwissRe microservice stopped and cleaned up!"
