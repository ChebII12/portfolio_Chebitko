#!/bin/bash

# First Aid AI - Production Deployment Script
# This script deploys the application to production

set -e

echo "🚀 Deploying First Aid AI to Production"

# Configuration
DEPLOY_ENV=${1:-production}
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
check_requirements() {
    log_info "Checking deployment requirements..."

    # Check if required environment variables are set
    required_vars=("BIGQUERY_PROJECT_ID" "BIGQUERY_CREDENTIALS_PATH" "SECRET_KEY" "GROQ_API_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    log_info "Requirements check passed"
}

create_backup() {
    log_info "Creating deployment snapshot..."

    mkdir -p "$BACKUP_DIR"
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.prod.yml "$BACKUP_DIR/" 2>/dev/null || true

    log_info "Snapshot created at $BACKUP_DIR"
}

# Deploy application
deploy() {
    log_info "Starting deployment..."

    # Pull latest images and build the application stack
    log_info "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull

    log_info "Building custom images..."
    docker-compose -f docker-compose.prod.yml build --no-cache

    # Start services
    log_info "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d

    # Confirm BigQuery dataset/table access from the backend container
    log_info "Validating BigQuery access..."
    docker-compose -f docker-compose.prod.yml exec -T backend python -c "from app.core.bigquery_service import get_bq_service; s = get_bq_service(); print(s.get_user_profile_by_email('deployment-check@example.invalid') is None)"

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
            log_info "All services are healthy"
            break
        fi

        log_info "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        log_error "Services failed to become healthy"
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Performing health checks..."

    # Check backend
    if ! curl -f --max-time 10 http://localhost/api/health; then
        log_error "Backend health check failed"
        exit 1
    fi

    # Check frontend
    if ! curl -f --max-time 10 http://localhost; then
        log_error "Frontend health check failed"
        exit 1
    fi

    log_info "Health checks passed"
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."

    # Stop current deployment
    docker-compose -f docker-compose.prod.yml down

    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ]; then
        log_info "Restoring from backup..."
        cp "$BACKUP_DIR/.env" . 2>/dev/null || true
        # Additional rollback logic would go here
    fi

    log_error "Rollback completed. Manual intervention may be required."
    exit 1
}

# Main deployment process
main() {
    log_info "Starting production deployment for environment: $DEPLOY_ENV"

    check_requirements
    create_backup

    # Set trap for rollback on error
    trap rollback ERR

    deploy
    health_check

    log_info "🎉 Deployment completed successfully!"
    log_info ""
    log_info "Application URLs:"
    log_info "  Frontend: https://yourdomain.com"
    log_info "  Backend API: https://yourdomain.com/api"
    log_info "  Health Check: https://yourdomain.com/api/health"
    log_info ""
    log_info "Monitoring:"
    log_info "  Grafana: https://yourdomain.com:3000"
    log_info "  Prometheus: https://yourdomain.com:9090"
    log_info ""
    log_info "Snapshot location: $BACKUP_DIR"
}

# Run main function
main "$@"
