#!/bin/bash

echo "=== Cash Pro Setup Test ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo "✅ Docker is installed"

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker Compose is installed"
echo ""

# Check if services are running
echo "Checking Docker services..."
if docker ps | grep -q cash_pro_postgres; then
    echo "✅ PostgreSQL container is running"
else
    echo "⚠️  PostgreSQL container is not running"
fi

if docker ps | grep -q cash_pro_backend; then
    echo "✅ Backend container is running"
else
    echo "⚠️  Backend container is not running"
fi

echo ""
echo "=== Testing API ==="
echo ""

# Test health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ] && echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding. Make sure docker-compose up is running."
    echo "   Try: docker-compose up -d"
fi

echo ""
echo "=== Testing Frontend ==="
echo ""

# Check if frontend dependencies are installed
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies are installed"
else
    echo "⚠️  Frontend dependencies not installed. Run: cd frontend && npm install"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Start services: docker-compose up -d"
echo "2. Install frontend: cd frontend && npm install"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Access frontend: http://localhost:5173"
echo "5. Access API docs: http://localhost:8000/docs"
echo ""

