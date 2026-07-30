#!/bin/bash

# First Aid AI - Rollback Script
# This script rolls back to the previous deployment

set -e

echo "🔄 Rolling back First Aid AI deployment"

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

# Find latest backup
find_latest_backup() {
    LATEST_BACKUP=$(find ./backups -maxdepth 1 -type d -name "20*" | sort | tail -1)
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found"
        exit 1
    fi
    log_info "Found latest backup: $LATEST_BACKUP"
}

# Stop current services
stop_services() {
    log_info "Stopping current services..."
    docker-compose -f docker-compose.prod.yml down
}

# Restore from backup
restore_backup() {
    log_info "Restoring from backup..."

    # Restore environment file
    if [ -f "$LATEST_BACKUP/.env" ]; then
        cp "$LATEST_BACKUP/.env" .
        log_info "Environment file restored"
    fi

    # BigQuery rollback is config-based: keep writes off and reads on legacy until revalidated.
    export BIGQUERY_WRITE_ENABLED=false
    export BIGQUERY_READ_SOURCE=legacy
    log_info "BigQuery rollback flags applied"
}

# Start services
start_services() {
    log_info "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
}

# Health check
health_check() {
    log_info "Performing health checks..."

    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f --max-time 10 http://localhost/api/health && curl -f --max-time 10 http://localhost; then
            log_info "Health checks passed"
            return 0
        fi

        log_info "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Main rollback process
main() {
    log_warn "This will rollback the application to the previous version"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    find_latest_backup
    stop_services
    restore_backup
    start_services

    if health_check; then
        log_info "🎉 Rollback completed successfully!"
        log_info "Application should now be running the previous version with BigQuery writes disabled"
    else
        log_error "❌ Rollback completed but health checks failed"
        log_error "Manual intervention may be required"
        exit 1
    fi
}

# Run main function
main "$@"
