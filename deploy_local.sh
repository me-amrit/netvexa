#!/bin/bash

echo "========================================="
echo "NETVEXA Local Deployment"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
    echo -e "${GREEN}✓ Python3 found: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python3 not found. Please install Python 3.8 or higher${NC}"
    exit 1
fi

# Check Node.js
if command_exists node; then
    echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 16 or higher${NC}"
    exit 1
fi

# Check PostgreSQL
if command_exists psql; then
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
else
    echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL${NC}"
    exit 1
fi

# Check if ports are available
if port_in_use 8000; then
    echo -e "${RED}✗ Port 8000 is already in use. Please stop the service using it.${NC}"
    exit 1
fi

if port_in_use 3000; then
    echo -e "${RED}✗ Port 3000 is already in use. Please stop the service using it.${NC}"
    exit 1
fi

echo -e "${GREEN}All prerequisites met!${NC}"

# Function to run backend
run_backend() {
    echo -e "\n${YELLOW}Starting Backend...${NC}"
    cd backend
    if [ -f "run_backend.sh" ]; then
        ./run_backend.sh
    else
        echo -e "${RED}Backend run script not found!${NC}"
        exit 1
    fi
}

# Function to run frontend
run_frontend() {
    echo -e "\n${YELLOW}Starting Frontend...${NC}"
    cd dashboard
    if [ -f "run_frontend.sh" ]; then
        ./run_frontend.sh
    else
        echo -e "${RED}Frontend run script not found!${NC}"
        exit 1
    fi
}

# Main menu
echo -e "\n${YELLOW}What would you like to start?${NC}"
echo "1) Backend only"
echo "2) Frontend only"  
echo "3) Both (recommended)"
echo "4) Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        run_backend
        ;;
    2)
        run_frontend
        ;;
    3)
        # Start backend in background
        echo -e "${YELLOW}Starting backend in background...${NC}"
        (cd backend && ./run_backend.sh) &
        BACKEND_PID=$!
        
        # Wait for backend to start
        echo -e "${YELLOW}Waiting for backend to start...${NC}"
        sleep 5
        
        # Check if backend is running
        if curl -f http://localhost:8000/ >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is running${NC}"
        else
            echo -e "${YELLOW}Backend might still be starting...${NC}"
        fi
        
        # Start frontend
        echo -e "\n${YELLOW}Starting frontend...${NC}"
        cd dashboard && ./run_frontend.sh
        
        # When frontend is stopped, also stop backend
        kill $BACKEND_PID 2>/dev/null
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac