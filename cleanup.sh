#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}NETVEXA Cleanup Script${NC}"
    echo ""
    echo "Usage: ./cleanup.sh [option]"
    echo ""
    echo "Options:"
    echo "  ports     - Kill processes on ports 3000, 8000"
    echo "  docker    - Stop and remove Docker containers"
    echo "  deps      - Clean dependencies (node_modules, venv)"
    echo "  data      - Remove database data (WARNING: Deletes all data!)"
    echo "  logs      - Clean log files"
    echo "  all       - Clean everything except data"
    echo "  full      - Clean everything including data (DANGEROUS!)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./cleanup.sh ports    # Free up ports"
    echo "  ./cleanup.sh docker   # Stop Docker containers"
    echo "  ./cleanup.sh all      # Clean everything safely"
}

# Function to kill processes on ports
cleanup_ports() {
    echo -e "${YELLOW}Cleaning up ports...${NC}"
    
    # Kill process on port 3000 (frontend)
    if lsof -ti:3000 >/dev/null 2>&1; then
        lsof -ti:3000 | xargs kill -9
        echo -e "${GREEN}✓ Freed port 3000${NC}"
    else
        echo -e "${BLUE}Port 3000 is already free${NC}"
    fi
    
    # Kill process on port 8000 (backend)
    if lsof -ti:8000 >/dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9
        echo -e "${GREEN}✓ Freed port 8000${NC}"
    else
        echo -e "${BLUE}Port 8000 is already free${NC}"
    fi
}

# Function to stop Docker containers
cleanup_docker() {
    echo -e "${YELLOW}Stopping Docker containers...${NC}"
    
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose down
        echo -e "${GREEN}✓ Docker containers stopped${NC}"
    else
        echo -e "${RED}docker-compose not found${NC}"
    fi
}

# Function to clean dependencies
cleanup_deps() {
    echo -e "${YELLOW}Cleaning dependencies...${NC}"
    
    # Clean Python virtual environment
    if [ -d "backend/venv" ]; then
        rm -rf backend/venv
        echo -e "${GREEN}✓ Removed Python virtual environment${NC}"
    fi
    
    # Clean Python cache
    find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find backend -type f -name "*.pyc" -delete 2>/dev/null
    echo -e "${GREEN}✓ Cleaned Python cache${NC}"
    
    # Clean Node modules
    if [ -d "dashboard/node_modules" ]; then
        rm -rf dashboard/node_modules
        echo -e "${GREEN}✓ Removed node_modules${NC}"
    fi
    
    # Clean package-lock
    if [ -f "dashboard/package-lock.json" ]; then
        rm -f dashboard/package-lock.json
        echo -e "${GREEN}✓ Removed package-lock.json${NC}"
    fi
}

# Function to clean data (DANGEROUS!)
cleanup_data() {
    echo -e "${RED}WARNING: This will delete all database data!${NC}"
    read -p "Are you sure? Type 'yes' to continue: " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${YELLOW}Cancelled${NC}"
        return
    fi
    
    echo -e "${YELLOW}Removing database volumes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Database data removed${NC}"
}

# Function to clean logs
cleanup_logs() {
    echo -e "${YELLOW}Cleaning log files...${NC}"
    
    # Clean backend logs
    find backend -name "*.log" -delete 2>/dev/null
    
    # Clean npm logs
    rm -rf ~/.npm/_logs/* 2>/dev/null
    
    echo -e "${GREEN}✓ Log files cleaned${NC}"
}

# Function to check what's running
check_status() {
    echo -e "${BLUE}Current Status:${NC}"
    echo ""
    
    # Check ports
    echo -e "${YELLOW}Ports:${NC}"
    if lsof -ti:3000 >/dev/null 2>&1; then
        echo -e "  Port 3000: ${RED}IN USE${NC} (Frontend)"
    else
        echo -e "  Port 3000: ${GREEN}FREE${NC}"
    fi
    
    if lsof -ti:8000 >/dev/null 2>&1; then
        echo -e "  Port 8000: ${RED}IN USE${NC} (Backend)"
    else
        echo -e "  Port 8000: ${GREEN}FREE${NC}"
    fi
    
    # Check Docker
    echo -e "\n${YELLOW}Docker Containers:${NC}"
    if docker ps | grep -q "netvexa"; then
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep netvexa
    else
        echo -e "  ${GREEN}No NETVEXA containers running${NC}"
    fi
}

# Main script logic
case "${1:-help}" in
    ports)
        cleanup_ports
        ;;
    docker)
        cleanup_docker
        ;;
    deps)
        cleanup_deps
        ;;
    data)
        cleanup_data
        ;;
    logs)
        cleanup_logs
        ;;
    all)
        cleanup_ports
        cleanup_docker
        cleanup_deps
        cleanup_logs
        echo -e "${GREEN}✓ Cleanup complete (data preserved)${NC}"
        ;;
    full)
        echo -e "${RED}FULL CLEANUP - This will delete everything including data!${NC}"
        read -p "Are you absolutely sure? Type 'DELETE ALL' to continue: " confirmation
        
        if [ "$confirmation" != "DELETE ALL" ]; then
            echo -e "${YELLOW}Cancelled${NC}"
            exit 0
        fi
        
        cleanup_ports
        cleanup_docker
        cleanup_deps
        cleanup_data
        cleanup_logs
        echo -e "${GREEN}✓ Full cleanup complete${NC}"
        ;;
    status)
        check_status
        ;;
    help|--help|-h|"")
        usage
        ;;
    *)
        echo -e "${RED}Invalid option: $1${NC}"
        usage
        exit 1
        ;;
esac