#!/bin/bash

# First Aid AI - Development Environment Setup
# This script sets up the development environment

set -e

echo "🚀 Setting up First Aid AI Development Environment"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update the .env file with your actual values before continuing."
    echo "   Required: BIGQUERY_PROJECT_ID, BIGQUERY_CREDENTIALS_PATH, SECRET_KEY"
    read -p "Press enter when you've updated the .env file..."
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Validate BigQuery connectivity
echo "🗄️  Validating BigQuery connectivity..."
docker-compose exec backend python -c "from app.core.bigquery_service import get_bq_service; s = get_bq_service(); print(s.create_dataset_and_tables())"

# Check if services are running
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/api/health &>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi

if curl -f http://localhost:3000 &>/dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "☁️  BigQuery dataset: first_aid_ai_module1"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
