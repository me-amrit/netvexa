#!/bin/bash

echo "NETVEXA Deployment Test"
echo "======================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test backend
echo -e "\n${YELLOW}Testing Backend...${NC}"

# Check if backend is running
if curl -s http://localhost:8000/ | grep -q "NETVEXA"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
    
    # Check API docs
    if curl -s http://localhost:8000/docs | grep -q "FastAPI"; then
        echo -e "${GREEN}✓ API documentation available${NC}"
    else
        echo -e "${RED}✗ API documentation not accessible${NC}"
    fi
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "  Please run: cd backend && ./run_backend.sh"
fi

# Test frontend
echo -e "\n${YELLOW}Testing Frontend...${NC}"

# Check if frontend is running
if curl -s http://localhost:3000/ | grep -q "React"; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo "  Please run: cd dashboard && ./run_frontend.sh"
fi

# Test database
echo -e "\n${YELLOW}Testing Database...${NC}"

if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    
    # Check if database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw netvexa; then
        echo -e "${GREEN}✓ Database 'netvexa' exists${NC}"
    else
        echo -e "${RED}✗ Database 'netvexa' not found${NC}"
        echo "  Please run: createdb netvexa"
    fi
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
fi

echo -e "\n${YELLOW}Summary:${NC}"
echo "Backend URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend URL: http://localhost:3000"
echo ""
echo "To deploy everything at once, run: ./deploy_local.sh"