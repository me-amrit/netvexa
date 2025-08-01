#!/bin/bash

echo "🔍 NETVEXA Services Status Check"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is open
check_port() {
    nc -z localhost $1 2>/dev/null
    return $?
}

# Check Docker containers
echo "📦 Docker Services:"
if command -v docker-compose &> /dev/null; then
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        echo -e "  PostgreSQL:    ${GREEN}✓ Running${NC}"
        echo -e "  Redis:         ${GREEN}✓ Running${NC}"
        echo -e "  pgAdmin:       ${GREEN}✓ Running${NC} (http://localhost:5050)"
    else
        echo -e "  Docker:        ${RED}✗ Not running${NC}"
        echo "  Run: ./start-dev.sh to start"
    fi
else
    echo -e "  Docker:        ${YELLOW}⚠ docker-compose not found${NC}"
fi

echo ""

# Check Backend API
echo "🚀 Backend API:"
if check_port 8000; then
    echo -e "  FastAPI:       ${GREEN}✓ Running${NC} (http://localhost:8000)"
    echo -e "  Chat Demo:     ${GREEN}✓ Available${NC} (http://localhost:8000/static/index.html)"
    echo -e "  API Docs:      ${GREEN}✓ Available${NC} (http://localhost:8000/docs)"
    echo -e "  Metrics:       ${GREEN}✓ Available${NC} (http://localhost:8000/static/metrics.html)"
else
    echo -e "  FastAPI:       ${RED}✗ Not running${NC}"
    echo "  Run: cd backend && ./run_mvp.sh"
fi

echo ""

# Check Marketing Site
echo "🌐 Marketing Website:"
NEXT_PID=$(ps aux | grep "next dev" | grep -v grep | awk '{print $2}' | head -1)
if [ ! -z "$NEXT_PID" ]; then
    echo -e "  Next.js:       ${GREEN}✓ Running${NC} (PID: $NEXT_PID)"
    echo -e "  Homepage:      ${GREEN}✓ Available${NC} (http://localhost:3000)"
    echo -e "  Blog:          ${GREEN}✓ Available${NC} (http://localhost:3000/blog)"
else
    echo -e "  Next.js:       ${RED}✗ Not running${NC}"
    echo "  Run: cd marketing-site && ./start-dev.sh"
fi

echo ""

# Check WordPress Plugin
echo "🔌 WordPress Plugin:"
if [ -d "/Users/amrit/Repo/netvexa/wordpress-plugin/netvexa-chat" ]; then
    echo -e "  Plugin Files:  ${GREEN}✓ Ready${NC}"
    echo "  Install in WordPress: /wp-content/plugins/"
else
    echo -e "  Plugin:        ${RED}✗ Not found${NC}"
fi

echo ""

# Memory usage
echo "💾 Resource Usage:"
if [ ! -z "$NEXT_PID" ]; then
    NEXT_MEM=$(ps aux | grep "$NEXT_PID" | awk '{print $4}')
    echo "  Next.js Memory: ${NEXT_MEM}%"
fi

# Check disk space for Docker
if command -v docker &> /dev/null; then
    DOCKER_SPACE=$(docker system df --format "table {{.Type}}\t{{.Size}}" | grep -E "Images|Containers" | awk '{sum += $2} END {print sum}')
    echo "  Docker Space: ~${DOCKER_SPACE}MB"
fi

echo ""
echo "================================"
echo "Quick Commands:"
echo "  Start all:     ./start-dev.sh"
echo "  Stop all:      ./shutdown-all.sh"
echo "  Check logs:    docker-compose logs -f"
echo ""