#!/bin/bash

# InsightPulse ERP Configuration CLI Helper
# This script provides quick access to common ERP configuration tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running on production server
is_production() {
    if [ -f "/opt/odoo-ce/docker-compose.prod.yml" ]; then
        return 0
    else
        return 1
    fi
}

# Function to access Odoo shell
odoo_shell() {
    print_info "Accessing Odoo shell..."
    if is_production; then
        docker compose -f docker-compose.prod.yml exec odoo odoo-bin shell -c /etc/odoo.conf -d odoo
    else
        docker compose exec odoo odoo-bin shell -c /etc/odoo.conf -d odoo
    fi
}

# Function to test database connectivity
test_db_connection() {
    print_info "Testing database connectivity..."
    if is_production; then
        docker exec odoo-db-1 psql -U odoo -d odoo -c 'SELECT version();'
    else
        docker exec odoo-db psql -U odoo -d odoo -c 'SELECT version();'
    fi
    print_success "Database connection successful"
}

# Function to check container status
check_containers() {
    print_info "Checking container status..."
    if is_production; then
        docker compose -f docker-compose.prod.yml ps
    else
        docker compose ps
    fi
}

# Function to restart Odoo service
restart_odoo() {
    print_info "Restarting Odoo service..."
    if is_production; then
        docker compose -f docker-compose.prod.yml restart odoo
    else
        docker compose restart odoo
    fi
    print_success "Odoo service restarted"
}

# Function to view Odoo logs
view_logs() {
    print_info "Viewing Odoo logs..."
    if is_production; then
        docker compose -f docker-compose.prod.yml logs odoo -f
    else
        docker compose logs odoo -f
    fi
}

# Function to update system parameter via CLI
update_system_param() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        print_error "Usage: $0 update-param <key> <value>"
        exit 1
    fi
    
    KEY="$1"
    VALUE="$2"
    
    print_info "Updating system parameter: $KEY = $VALUE"
    
    # Create Python script for parameter update
    cat > /tmp/update_param.py << EOF
env['ir.config_parameter'].set_param('$KEY', '$VALUE')
env.cr.commit()
print("✅ System parameter updated: $KEY = $VALUE")
EOF
    
    # Execute the update
    if is_production; then
        docker compose -f docker-compose.prod.yml exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/update_param.py
    else
        docker compose exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/update_param.py
    fi
    
    # Clean up
    rm -f /tmp/update_param.py
}

# Function to reset admin password
reset_admin_password() {
    if [ -z "$1" ]; then
        print_error "Usage: $0 reset-password <new_password>"
        exit 1
    fi
    
    NEW_PASSWORD="$1"
    
    print_info "Resetting admin password..."
    
    # Create Python script for password reset
    cat > /tmp/reset_password.py << EOF
admin = env['res.users'].search([('login', '=', 'admin')])
if admin:
    admin.password = '$NEW_PASSWORD'
    env.cr.commit()
    print("✅ Admin password reset successfully")
else:
    print("❌ Admin user not found")
EOF
    
    # Execute the reset
    if is_production; then
        docker compose -f docker-compose.prod.yml exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/reset_password.py
    else
        docker compose exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/reset_password.py
    fi
    
    # Clean up
    rm -f /tmp/reset_password.py
}

# Function to show current configuration
show_config() {
    print_info "Current ERP Configuration:"
    echo ""
    echo "=== Database Configuration ==="
    test_db_connection
    echo ""
    
    echo "=== Container Status ==="
    check_containers
    echo ""
    
    echo "=== Common System Parameters ==="
    # Create Python script to show parameters
    cat > /tmp/show_params.py << EOF
params = [
    'web.base.url',
    'ai.ocr.api.key',
    'ocr.service.endpoint',
    'payout.n8n.webhook'
]

for param in params:
    value = env['ir.config_parameter'].get_param(param)
    if value:
        print(f"{param}: {value}")
    else:
        print(f"{param}: [Not Set]")
EOF
    
    if is_production; then
        docker compose -f docker-compose.prod.yml exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/show_params.py
    else
        docker compose exec -T odoo odoo-bin shell -c /etc/odoo.conf -d odoo < /tmp/show_params.py
    fi
    
    rm -f /tmp/show_params.py
}

# Function to display help
show_help() {
    echo "InsightPulse ERP Configuration CLI Helper"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  shell                    Access Odoo interactive shell"
    echo "  test-db                  Test database connectivity"
    echo "  status                   Check container status"
    echo "  restart-odoo             Restart Odoo service"
    echo "  logs                     View Odoo logs (follow mode)"
    echo "  update-param <key> <value>  Update system parameter"
    echo "  reset-password <new_pass>   Reset admin password"
    echo "  show-config              Show current configuration"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test-db"
    echo "  $0 update-param web.base.url https://erp.insightpulseai.net"
    echo "  $0 reset-password mynewpassword123"
    echo ""
}

# Main command handler
case "$1" in
    "shell")
        odoo_shell
        ;;
    "test-db")
        test_db_connection
        ;;
    "status")
        check_containers
        ;;
    "restart-odoo")
        restart_odoo
        ;;
    "logs")
        view_logs
        ;;
    "update-param")
        update_system_param "$2" "$3"
        ;;
    "reset-password")
        reset_admin_password "$2"
        ;;
    "show-config")
        show_config
        ;;
    "help"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
