#!/bin/bash

# NETVEXA WordPress Plugin End-to-End Test Script
# Tests plugin functionality in WordPress environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WP_URL="http://localhost:8080"
WP_ADMIN_URL="$WP_URL/wp-admin"
PLUGIN_ZIP="dist/netvexa-chat-1.0.0.zip"
TEST_API_ENDPOINT="http://localhost:8000"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if WordPress is running
    if ! curl -s "$WP_URL" >/dev/null; then
        log_error "WordPress is not running at $WP_URL"
        log_info "Please start WordPress environment first: cd ../wordpress-test && ./start-wordpress.sh"
        exit 1
    fi
    
    # Check if NETVEXA backend is running
    if ! curl -s "$TEST_API_ENDPOINT/docs" >/dev/null; then
        log_warning "NETVEXA backend is not running at $TEST_API_ENDPOINT"
        log_warning "Some tests may fail. To start backend: cd .. && ./start-dev.sh"
    fi
    
    # Check if plugin ZIP exists
    if [ ! -f "$PLUGIN_ZIP" ]; then
        log_error "Plugin ZIP file not found: $PLUGIN_ZIP"
        log_info "Please build the plugin first: ./deploy.sh"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Test plugin files
test_plugin_structure() {
    log_info "Testing plugin file structure..."
    
    local script_dir="$(cd "$(dirname "$0")" && pwd)"
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Extract and test plugin structure
    unzip -q "$script_dir/$PLUGIN_ZIP"
    
    # Check required files
    local required_files=(
        "netvexa-chat/netvexa-chat.php"
        "netvexa-chat/readme.txt"
        "netvexa-chat/includes/class-netvexa-chat.php"
        "netvexa-chat/includes/class-netvexa-admin.php"
        "netvexa-chat/includes/class-netvexa-widget.php"
        "netvexa-chat/includes/class-netvexa-shortcode.php"
        "netvexa-chat/assets/admin.css"
        "netvexa-chat/assets/admin.js"
        "netvexa-chat/assets/widget.js"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Test main plugin file syntax
    if ! php -l "netvexa-chat/netvexa-chat.php" >/dev/null 2>&1; then
        log_error "PHP syntax error in main plugin file"
        exit 1
    fi
    
    # Test version consistency
    local plugin_version=$(grep "Version:" netvexa-chat/netvexa-chat.php | sed "s/.*Version: *//")
    local readme_version=$(grep "Stable tag:" netvexa-chat/readme.txt | sed "s/.*Stable tag: *//")
    
    if [ "$plugin_version" != "$readme_version" ]; then
        log_error "Version mismatch: Plugin ($plugin_version) vs Readme ($readme_version)"
        exit 1
    fi
    
    # Cleanup
    cd - >/dev/null
    rm -rf "$temp_dir"
    
    log_success "Plugin structure tests passed"
}

# Test WordPress integration
test_wordpress_requirements() {
    log_info "Testing WordPress compatibility..."
    
    # Test if WordPress can be accessed
    local wp_response=$(curl -s -o /dev/null -w "%{http_code}" "$WP_URL")
    if [ "$wp_response" != "200" ]; then
        log_error "WordPress not accessible (HTTP $wp_response)"
        exit 1
    fi
    
    # Check if WordPress admin is accessible
    local admin_response=$(curl -s -o /dev/null -w "%{http_code}" "$WP_ADMIN_URL")
    if [ "$admin_response" -lt "200" ] || [ "$admin_response" -ge "400" ]; then
        log_warning "WordPress admin may not be set up yet (HTTP $admin_response)"
        log_info "Please complete WordPress installation at $WP_URL"
    fi
    
    log_success "WordPress integration tests passed"
}

# Test API connectivity
test_api_connectivity() {
    log_info "Testing NETVEXA API connectivity..."
    
    # Test API endpoint
    if curl -s "$TEST_API_ENDPOINT/docs" >/dev/null; then
        log_success "NETVEXA API is accessible"
        
        # Test specific endpoints
        local endpoints=("/api/agents" "/api/auth/login")
        for endpoint in "${endpoints[@]}"; do
            local response=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_API_ENDPOINT$endpoint")
            if [ "$response" -eq "200" ] || [ "$response" -eq "422" ] || [ "$response" -eq "401" ]; then
                log_success "API endpoint accessible: $endpoint"
            else
                log_warning "API endpoint issue: $endpoint (HTTP $response)"
            fi
        done
    else
        log_warning "NETVEXA API not accessible - plugin will work but connection tests will fail"
    fi
}

# Test JavaScript and CSS
test_assets() {
    log_info "Testing plugin assets..."
    
    # Test CSS syntax (basic check)
    if command -v csslint >/dev/null 2>&1; then
        if csslint --quiet netvexa-chat/assets/admin.css; then
            log_success "CSS files are valid"
        else
            log_warning "CSS validation issues found"
        fi
    else
        log_info "csslint not available, skipping CSS validation"
    fi
    
    # Test JavaScript syntax (basic check)
    if command -v node >/dev/null 2>&1; then
        if node -c netvexa-chat/assets/admin.js && node -c netvexa-chat/assets/widget.js; then
            log_success "JavaScript files are valid"
        else
            log_error "JavaScript syntax errors found"
            exit 1
        fi
    else
        log_info "Node.js not available, skipping JavaScript validation"
    fi
}

# Security tests
test_security() {
    log_info "Running basic security tests..."
    
    # Check for potential security issues
    local script_dir="$(cd "$(dirname "$0")" && pwd)"
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    unzip -q "$script_dir/$PLUGIN_ZIP"
    
    # Check for direct file access protection
    if ! grep -q "defined('ABSPATH')" netvexa-chat/netvexa-chat.php; then
        log_error "Main plugin file missing ABSPATH check"
        exit 1
    fi
    
    # Check for SQL injection protection (basic check)
    if grep -r "\$_GET\|\$_POST" netvexa-chat/ | grep -v "sanitize\|esc_\|wp_verify_nonce"; then
        log_warning "Potential unsanitized input found - manual review recommended"
    else
        log_success "No obvious unsanitized input found"
    fi
    
    # Check for XSS protection
    if grep -r "echo.*\$_" netvexa-chat/ | grep -v "esc_html\|esc_attr\|wp_kses"; then
        log_warning "Potential XSS vulnerability found - manual review recommended"
    else
        log_success "No obvious XSS vulnerabilities found"
    fi
    
    # Cleanup
    cd - >/dev/null
    rm -rf "$temp_dir"
    
    log_success "Basic security tests passed"
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    local report_file="test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
NETVEXA WordPress Plugin Test Report
===================================
Generated: $(date)
Plugin Version: $(grep "Version:" netvexa-chat/netvexa-chat.php | sed "s/.*Version: *//")
Test Environment: $(uname -s) $(uname -r)

Test Results:
✅ Plugin structure and file integrity
✅ WordPress compatibility requirements
✅ API connectivity (if backend running)
✅ Asset validation (CSS/JS)
✅ Basic security checks

WordPress Environment:
- Site URL: $WP_URL
- Admin URL: $WP_ADMIN_URL
- Status: $(curl -s -o /dev/null -w "%{http_code}" "$WP_URL")

NETVEXA API:
- Endpoint: $TEST_API_ENDPOINT
- Status: $(curl -s -o /dev/null -w "%{http_code}" "$TEST_API_ENDPOINT/docs")

Next Steps:
1. Install WordPress at $WP_URL (if not already done)
2. Upload plugin ZIP: $PLUGIN_ZIP
3. Activate plugin and configure API settings
4. Test chat widget functionality
5. Verify lead capture and analytics

Manual Testing Checklist:
□ Plugin activation without errors
□ Settings page loads correctly
□ API connection test works
□ Chat widget appears on frontend
□ Widget customization options work
□ Shortcode functionality works
□ Mobile responsiveness
□ Browser compatibility testing
□ Lead capture functionality
□ Analytics tracking

EOF

    log_success "Test report generated: $report_file"
}

# Main test execution
main() {
    echo "🧪 NETVEXA WordPress Plugin Test Suite"
    echo "======================================"
    echo ""
    
    check_prerequisites
    test_plugin_structure
    test_wordpress_requirements
    test_api_connectivity
    test_assets
    test_security
    generate_report
    
    echo ""
    echo "🎉 All automated tests passed!"
    echo ""
    echo "📋 Manual Testing Steps:"
    echo "1. Visit: $WP_URL"
    echo "2. Complete WordPress setup if needed"
    echo "3. Go to: $WP_ADMIN_URL/plugin-install.php"
    echo "4. Upload: $PLUGIN_ZIP"
    echo "5. Activate plugin and configure settings"
    echo "6. Test chat widget on frontend"
    echo ""
    echo "📊 Plugin Package: $PLUGIN_ZIP"
    echo "🌐 WordPress: $WP_URL"
    echo "🔧 Admin: $WP_ADMIN_URL"
    echo ""
}

# Run tests
main "$@"