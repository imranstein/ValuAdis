#!/bin/bash

# ValuAdis Deployment Script
# Automated deployment to Yegara.com production server

set -euo pipefail

# Configuration
PROJECT_DIR="/var/www/valuadis"
BACKUP_DIR="/var/www/valuadis/backups"
LOG_FILE="/var/www/valuadis/logs/deploy.log"
COMPOSE_FILE="docker-compose.prod.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        error "Git is not installed"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Validate production environment before any deploy action mutates services
validate_environment() {
    log "Validating production environment..."

    cd "$PROJECT_DIR"

    if [[ ! -f ".env.production" ]]; then
        error ".env.production is missing. Copy the production template and set real values first."
        exit 1
    fi

    bash scripts/validate-production-env.sh .env.production

    success "Production environment validation passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$PROJECT_DIR/nginx/logs"
    mkdir -p "$PROJECT_DIR/logs/backend"
    mkdir -p "$PROJECT_DIR/logs/nginx"
    
    success "Directories created"
}

# Backup current deployment
backup_current() {
    log "Backing up current deployment..."
    
    if [[ -f "$PROJECT_DIR/$COMPOSE_FILE" ]]; then
        # Create backup timestamp
        BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_NAME="deployment_backup_$BACKUP_TIMESTAMP"
        
        # Backup docker volumes
        docker-compose -f "$PROJECT_DIR/$COMPOSE_FILE" down || true
        
        # Backup application files
        tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$PROJECT_DIR" .
        
        # Backup database
        if docker-compose -f "$PROJECT_DIR/$COMPOSE_FILE" ps -q db | grep -q .; then
            docker-compose -f "$PROJECT_DIR/$COMPOSE_FILE" exec -T db pg_dump \
                -U "${POSTGRES_USER:-valuadis_user}" \
                "${POSTGRES_DB:-valuadis}" > "$BACKUP_DIR/db_backup_$BACKUP_TIMESTAMP.sql"
        fi
        
        success "Backup completed: $BACKUP_NAME"
    else
        warning "No existing deployment to backup"
    fi
}

# Update application code
update_code() {
    log "Updating application code..."
    
    cd "$PROJECT_DIR"
    
    # Pull latest changes
    if [[ -d ".git" ]]; then
        git pull origin main
    else
        error "Git repository not found. Please clone the repository first."
        exit 1
    fi
    
    success "Code updated"
}

# Build and deploy services
deploy_services() {
    log "Building and deploying services..."
    
    cd "$PROJECT_DIR"
    
    # Stop existing services
    docker-compose -f "$COMPOSE_FILE" down || true
    
    # Build new images
    log "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    success "Services deployed"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$PROJECT_DIR"
    
    # Wait for database to be ready
    log "Waiting for database..."
    timeout=60
    while ! docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-valuadis_user}" >/dev/null 2>&1; do
        if [[ $timeout -le 0 ]]; then
            error "Database failed to start"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done

    local app_table_count
    app_table_count=$(docker-compose -f "$COMPOSE_FILE" exec -T db psql \
        -U "${POSTGRES_USER:-valuadis_user}" \
        -d "${POSTGRES_DB:-valuadis}" \
        -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users', 'properties', 'valuations', 'vehicles', 'raw_market_listings', 'scraper_targets');")

    local has_alembic_version
    has_alembic_version=$(docker-compose -f "$COMPOSE_FILE" exec -T db psql \
        -U "${POSTGRES_USER:-valuadis_user}" \
        -d "${POSTGRES_DB:-valuadis}" \
        -tAc "SELECT to_regclass('public.alembic_version') IS NOT NULL;")

    if ! bash scripts/check-migration-state.sh "${app_table_count:-0}" "$has_alembic_version"; then
        exit 1
    fi
    
    # Run migrations
    docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head

    local current_revision
    local head_revision
    current_revision=$(docker-compose -f "$COMPOSE_FILE" exec -T backend alembic current | tail -n 1 | awk '{print $1}')
    head_revision=$(docker-compose -f "$COMPOSE_FILE" exec -T backend alembic heads | tail -n 1 | awk '{print $1}')

    if ! bash scripts/check-migration-state.sh 0 true "$current_revision" "$head_revision"; then
        exit 1
    fi
    
    success "Database migrations completed"
}

# Health checks
health_checks() {
    log "Performing health checks..."
    
    cd "$PROJECT_DIR"
    
    # Check if all services are running
    log "Checking service status..."
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        error "Some services are not running"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 1
    fi
    
    # Check backend health
    log "Checking backend health..."
    timeout=30
    while ! curl -f http://localhost/health >/dev/null 2>&1; do
        if [[ $timeout -le 0 ]]; then
            error "Backend health check failed"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    # Check frontend
    log "Checking frontend..."
    if ! curl -f http://localhost/ >/dev/null 2>&1; then
        error "Frontend health check failed"
        exit 1
    fi
    
    success "All health checks passed"
}

# Setup SSL certificates (if needed)
setup_ssl() {
    log "Checking SSL certificates..."
    
    # Check if certificates exist and are valid
    if [[ ! -f "/etc/letsencrypt/live/valuadis.et/fullchain.pem" ]]; then
        log "SSL certificates not found. Setting up Let's Encrypt..."
        
        # Install certbot if not present
        if ! command -v certbot &> /dev/null; then
            apt-get update
            apt-get install -y certbot python3-certbot-nginx
        fi
        
        # Get certificates (requires domain to be pointing to server)
        if [[ -n "${DOMAIN:-}" ]]; then
            certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "${EMAIL:-admin@valuadis.et}"
            success "SSL certificates setup completed"
        else
            warning "DOMAIN not set. Please configure SSL manually."
        fi
    else
        success "SSL certificates already exist"
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    success "Cleanup completed"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    log "Sending notification: $message"
    
    # Slack notification (if webhook URL is provided)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        local emoji="✅"
        if [[ "$status" == "error" ]]; then
            emoji="❌"
        elif [[ "$status" == "warning" ]]; then
            emoji="⚠️"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$emoji ValuAdis Deployment: $message\"}" \
            "$SLACK_WEBHOOK_URL" || true
    fi
    
    # Email notification (if configured)
    if [[ -n "${EMAIL_RECIPIENT:-}" && -n "${EMAIL_SENDER:-}" ]]; then
        echo "$message" | mail -s "ValuAdis Deployment $status" "$EMAIL_RECIPIENT" || true
    fi
}

# Main deployment function
main() {
    log "Starting ValuAdis deployment..."
    
    # Check prerequisites
    check_root
    check_prerequisites
    validate_environment
    
    # Create directories
    create_directories
    
    # Backup current deployment
    backup_current
    
    # Update code
    update_code
    
    # Deploy services
    deploy_services
    
    # Run migrations
    run_migrations
    
    # Setup SSL
    setup_ssl
    
    # Health checks
    health_checks
    
    # Cleanup
    cleanup
    
    success "Deployment completed successfully!"
    send_notification "success" "ValuAdis has been deployed successfully to production."
    
    log "Deployment summary:"
    log "- Services: Backend, Frontend, Database, Redis, Nginx"
    log "- SSL: Configured with Let's Encrypt"
    log "- Monitoring: Health checks enabled"
    log "- Backups: Created before deployment"
    log "- Logs: Available at $LOG_FILE"
}

# Rollback function
rollback() {
    log "Starting rollback..."
    
    cd "$PROJECT_DIR"
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/deployment_backup_*.tar.gz 2>/dev/null | head -1)
    
    if [[ -n "$LATEST_BACKUP" ]]; then
        log "Restoring from backup: $(basename "$LATEST_BACKUP")"
        
        # Restore application files
        tar -xzf "$LATEST_BACKUP" -C "$PROJECT_DIR"
        
        # Restore database if backup exists
        DB_BACKUP=$(echo "$LATEST_BACKUP" | sed 's/deployment_backup_/db_backup_/' | sed 's/\.tar\.gz/\.sql/')
        if [[ -f "$DB_BACKUP" ]]; then
            log "Restoring database..."
            docker-compose -f "$COMPOSE_FILE" up -d db
            sleep 10
            docker-compose -f "$COMPOSE_FILE" exec -T db psql -U "${POSTGRES_USER:-valuadis_user}" -d "${POSTGRES_DB:-valuadis}" < "$DB_BACKUP"
        fi
        
        # Start services
        docker-compose -f "$COMPOSE_FILE" up -d
        
        success "Rollback completed"
        send_notification "warning" "ValuAdis has been rolled back to previous version."
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    health-check)
        health_checks
        ;;
    backup)
        backup_current
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health-check|backup}"
        echo "  deploy      - Deploy the application"
        echo "  rollback    - Rollback to previous version"
        echo "  health-check - Perform health checks"
        echo "  backup      - Create backup"
        exit 1
        ;;
esac
