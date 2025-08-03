#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}NETVEXA Start Script${NC}"
    echo ""
    echo "Usage: ./start.sh [option]"
    echo ""
    echo "Options:"
    echo "  docker    - Start Docker services (PostgreSQL, Redis)"
    echo "  backend   - Start backend API server"
    echo "  dashboard - Start admin dashboard (React)"
    echo "  homepage  - Start home page (Next.js)"
    echo "  all       - Start everything (default)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start.sh          # Start everything"
    echo "  ./start.sh docker   # Start only Docker services"
    echo "  ./start.sh backend  # Start only backend"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to start Docker services
start_docker() {
    echo -e "${YELLOW}Starting Docker services...${NC}"
    
    if ! command_exists docker; then
        echo -e "${RED}Docker is not installed or not running${NC}"
        return 1
    fi
    
    # Check if containers are already running
    if docker ps | grep -q "netvexa-postgres"; then
        echo -e "${GREEN}✓ PostgreSQL is already running${NC}"
    else
        docker-compose up -d postgres
        echo -e "${GREEN}✓ PostgreSQL started on port 5433${NC}"
    fi
    
    if docker ps | grep -q "netvexa-redis"; then
        echo -e "${GREEN}✓ Redis is already running${NC}"
    else
        docker-compose up -d redis
        echo -e "${GREEN}✓ Redis started on port 6379${NC}"
    fi
    
    # Wait for PostgreSQL to be ready
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo -n "."
        sleep 1
    done
    echo -e "\n${GREEN}✓ PostgreSQL is ready${NC}"
}

# Function to start backend
start_backend() {
    echo -e "${YELLOW}Starting Backend API...${NC}"
    
    cd backend
    
    # Check Python
    if ! command_exists python3; then
        echo -e "${RED}Python3 is not installed${NC}"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    # Check if dependencies are installed
    if ! python -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
        pip install email-validator  # Additional dependency
    fi
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "${RED}Backend .env file not found!${NC}"
        echo -e "${YELLOW}Creating default .env file...${NC}"
        cp .env.example .env 2>/dev/null || create_backend_env
    fi
    
    # Check if port is available
    if port_in_use 8000; then
        echo -e "${RED}Port 8000 is already in use${NC}"
        echo -e "${YELLOW}Kill existing process with: lsof -ti:8000 | xargs kill -9${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
    echo -e "${GREEN}API docs at http://localhost:8000/docs${NC}"
    uvicorn main:app --host 0.0.0.0 --port 8000
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}Starting Frontend...${NC}"
    
    cd dashboard
    
    # Check Node.js
    if ! command_exists node; then
        echo -e "${RED}Node.js is not installed${NC}"
        return 1
    fi
    
    # Install dependencies with legacy peer deps flag
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install --legacy-peer-deps
    fi
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating frontend .env file...${NC}"
        echo "REACT_APP_API_URL=http://localhost:8000" > .env
    fi
    
    # Check if port is available
    if port_in_use 3000; then
        echo -e "${RED}Port 3000 is already in use${NC}"
        echo -e "${YELLOW}Kill existing process with: lsof -ti:3000 | xargs kill -9${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting frontend on http://localhost:3000${NC}"
    npm start
}

# Function to create backend .env
create_backend_env() {
    cat > .env << EOL
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:netvexa_password@localhost:5433/netvexa_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=netvexa_password
POSTGRES_DB=netvexa_db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys (Update these!)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# LLM Configuration
LLM_PROVIDER=google
GOOGLE_MODEL=gemini-1.5-flash

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
EOL
}

# Main script logic
case "${1:-all}" in
    docker)
        start_docker
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        # Start Docker first
        start_docker
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to start Docker services${NC}"
            exit 1
        fi
        
        # Start backend in new terminal (macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            osascript -e 'tell app "Terminal" to do script "cd '"$PWD"' && ./start.sh backend"'
        else
            echo -e "${YELLOW}Please run './start.sh backend' in a new terminal${NC}"
        fi
        
        # Wait a bit for backend to start
        echo -e "${YELLOW}Waiting for backend to start...${NC}"
        sleep 5
        
        # Start frontend in new terminal (macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            osascript -e 'tell app "Terminal" to do script "cd '"$PWD"' && ./start.sh frontend"'
        else
            echo -e "${YELLOW}Please run './start.sh frontend' in a new terminal${NC}"
        fi
        
        echo -e "${GREEN}All services starting...${NC}"
        echo -e "${BLUE}Dashboard: http://localhost:3000${NC}"
        echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
        echo -e "${BLUE}pgAdmin: http://localhost:5050${NC}"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Invalid option: $1${NC}"
        usage
        exit 1
        ;;
esac