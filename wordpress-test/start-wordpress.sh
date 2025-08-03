#!/bin/bash

echo "🐳 Starting WordPress Test Environment for NETVEXA Plugin"
echo "========================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the wordpress-test directory"
    exit 1
fi

# Start the services
echo "🚀 Starting WordPress services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ WordPress test environment is ready!"
    echo ""
    echo "📍 Access URLs:"
    echo "   WordPress Site: http://localhost:8080"
    echo "   WordPress Admin: http://localhost:8080/wp-admin"
    echo "   Database Admin:  http://localhost:8081"
    echo ""
    echo "🔧 First-time setup:"
    echo "   1. Visit http://localhost:8080 to complete WordPress installation"
    echo "   2. Create admin user (recommended: admin/password123)"
    echo "   3. Login and activate the NETVEXA Chat plugin"
    echo "   4. Configure plugin settings in WordPress admin"
    echo ""
    echo "💡 Plugin files are mounted from: ../wordpress-plugin/netvexa-chat/"
    echo "    Changes to plugin files are automatically reflected."
    echo ""
    echo "🛑 To stop: docker-compose down"
    echo "🔄 To reset: docker-compose down -v && docker-compose up -d"
else
    echo "❌ Failed to start WordPress services"
    docker-compose logs
    exit 1
fi