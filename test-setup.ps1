# Cash Pro Setup Test Script for Windows

Write-Host "=== Cash Pro Setup Test ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "❌ .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green
Write-Host ""

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}

try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=cash_pro_postgres" --format "{{.Names}}" | Select-String "cash_pro_postgres"
$backendRunning = docker ps --filter "name=cash_pro_backend" --format "{{.Names}}" | Select-String "cash_pro_backend"

if ($postgresRunning) {
    Write-Host "✅ PostgreSQL container is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL container is not running" -ForegroundColor Yellow
}

if ($backendRunning) {
    Write-Host "✅ Backend container is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend container is not running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Testing API ===" -ForegroundColor Cyan
Write-Host ""

# Test health endpoint
Write-Host "Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200 -and $response.Content -like "*healthy*") {
        Write-Host "✅ Backend API is responding" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend API returned unexpected response" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend API is not responding. Make sure docker-compose up is running." -ForegroundColor Red
    Write-Host "   Try: docker-compose up -d" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Testing Frontend ===" -ForegroundColor Cyan
Write-Host ""

# Check if frontend dependencies are installed
if (Test-Path "frontend/node_modules") {
    Write-Host "✅ Frontend dependencies are installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend dependencies not installed. Run: cd frontend; npm install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start services: docker-compose up -d"
Write-Host "2. Install frontend: cd frontend; npm install"
Write-Host "3. Start frontend: cd frontend; npm run dev"
Write-Host "4. Access frontend: http://localhost:5173"
Write-Host "5. Access API docs: http://localhost:8000/docs"
Write-Host ""

