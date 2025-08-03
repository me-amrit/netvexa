#!/bin/bash

# NETVEXA WordPress Plugin Deployment Script
# Builds, packages, and deploys the WordPress plugin

set -e  # Exit on any error

# Configuration
PLUGIN_NAME="netvexa-chat"
PLUGIN_VERSION="1.0.0"
BUILD_DIR="build"
DIST_DIR="dist"
EXCLUDE_FILES=("*.log" "*.tmp" "node_modules" ".git" ".DS_Store" "Thumbs.db" "deploy.sh" "build" "dist")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -f "${PLUGIN_NAME}/${PLUGIN_NAME}.php" ]; then
    log_error "Plugin main file not found. Please run this script from the wordpress-plugin directory."
    exit 1
fi

log_info "Starting NETVEXA WordPress Plugin deployment..."

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# Create build directory structure
log_info "Creating build structure..."
cp -r "$PLUGIN_NAME" "$BUILD_DIR/"

# Remove development files
log_info "Removing development files..."
cd "$BUILD_DIR/$PLUGIN_NAME"

# Remove files that shouldn't be in the final package
for exclude in "${EXCLUDE_FILES[@]}"; do
    find . -name "$exclude" -exec rm -rf {} + 2>/dev/null || true
done

# Optimize files
log_info "Optimizing files..."

# Minify CSS files (if uglify-css is available)
if command -v cleancss >/dev/null 2>&1; then
    log_info "Minifying CSS files..."
    find assets -name "*.css" -not -name "*.min.css" -exec sh -c '
        for file; do
            output="${file%.css}.min.css"
            cleancss -o "$output" "$file" && mv "$output" "$file"
        done
    ' sh {} +
else
    log_warning "cleancss not found. Skipping CSS minification."
fi

# Minify JavaScript files (if uglify-js is available)
if command -v uglifyjs >/dev/null 2>&1; then
    log_info "Minifying JavaScript files..."
    find assets -name "*.js" -not -name "*.min.js" -exec sh -c '
        for file; do
            uglifyjs "$file" -o "$file.tmp" -c -m && mv "$file.tmp" "$file"
        done
    ' sh {} +
else
    log_warning "uglifyjs not found. Skipping JavaScript minification."
fi

# Update version numbers in files
log_info "Updating version numbers..."
cd ../..

# Update main plugin file
sed -i.bak "s/Version: [0-9.]\+/Version: $PLUGIN_VERSION/g" "$BUILD_DIR/$PLUGIN_NAME/$PLUGIN_NAME.php"
sed -i.bak "s/define('NETVEXA_VERSION', '[^']*')/define('NETVEXA_VERSION', '$PLUGIN_VERSION')/g" "$BUILD_DIR/$PLUGIN_NAME/$PLUGIN_NAME.php"

# Update readme.txt
if [ -f "$BUILD_DIR/$PLUGIN_NAME/readme.txt" ]; then
    sed -i.bak "s/Stable tag: [0-9.]\+/Stable tag: $PLUGIN_VERSION/g" "$BUILD_DIR/$PLUGIN_NAME/readme.txt"
fi

# Clean up backup files
find "$BUILD_DIR" -name "*.bak" -delete

# Create ZIP package
log_info "Creating ZIP package..."
cd "$BUILD_DIR"
zip -r "../$DIST_DIR/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" "$PLUGIN_NAME/" -x "*.DS_Store" "*.git*"
cd ..

# Create WordPress.org SVN-ready structure
log_info "Creating WordPress.org SVN structure..."
SVN_DIR="$DIST_DIR/svn"
mkdir -p "$SVN_DIR/trunk" "$SVN_DIR/tags/$PLUGIN_VERSION"

# Copy to trunk
cp -r "$BUILD_DIR/$PLUGIN_NAME/"* "$SVN_DIR/trunk/"

# Copy to tags
cp -r "$BUILD_DIR/$PLUGIN_NAME/"* "$SVN_DIR/tags/$PLUGIN_VERSION/"

# Generate checksums
log_info "Generating checksums..."
cd "$DIST_DIR"
sha256sum "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" > "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.sha256"
md5sum "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" > "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.md5"

# Create deployment info
cat > "deployment-info.json" << EOF
{
    "plugin_name": "$PLUGIN_NAME",
    "version": "$PLUGIN_VERSION",
    "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "build_system": "$(uname -s) $(uname -r)",
    "files": {
        "zip": "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip",
        "checksum_sha256": "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.sha256",
        "checksum_md5": "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.md5"
    },
    "wordpress_requirements": {
        "minimum_wp_version": "5.0",
        "tested_up_to": "6.4",
        "minimum_php_version": "7.4"
    }
}
EOF

cd ..

# Generate deployment summary
log_success "Deployment completed successfully!"
echo ""
echo "==============================================="
echo "  NETVEXA WordPress Plugin Deployment Summary"
echo "==============================================="
echo "Plugin: $PLUGIN_NAME"
echo "Version: $PLUGIN_VERSION"
echo "Build Date: $(date)"
echo ""
echo "Generated Files:"
echo "  📦 ZIP Package: $DIST_DIR/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip"
echo "  🔐 SHA256: $DIST_DIR/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.sha256"
echo "  🔐 MD5: $DIST_DIR/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip.md5"
echo "  📋 Info: $DIST_DIR/deployment-info.json"
echo "  📁 SVN Structure: $DIST_DIR/svn/"
echo ""
echo "Next Steps:"
echo "  1. Test the plugin: Upload $DIST_DIR/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip to a test WordPress site"
echo "  2. WordPress.org: Use $DIST_DIR/svn/ structure for WordPress.org repository"
echo "  3. Auto-updates: Upload files to your update server"
echo ""

# Optional: Start WordPress test environment
if [ -f "../wordpress-test/start-wordpress.sh" ]; then
    echo "💡 To test immediately, run:"
    echo "   cd ../wordpress-test && ./start-wordpress.sh"
    echo "   Then upload the ZIP file in WordPress admin."
fi

log_success "Plugin deployment completed! 🚀"