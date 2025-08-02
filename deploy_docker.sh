#!/bin/bash

echo "========================================="
echo "NETVEXA Docker Deployment"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}docker-compose is not installed.${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=netvexa_password
POSTGRES_DB=netvexa_db

# API Keys (Update these!)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# JWT
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)

# Environment
ENVIRONMENT=development
EOL
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please update the API keys in .env file${NC}"
fi

# Start PostgreSQL and Redis
echo -e "\n${YELLOW}Starting PostgreSQL and Redis...${NC}"
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo -n "."
    sleep 1
done
echo -e "\n${GREEN}✓ PostgreSQL is ready${NC}"

# Run backend locally (not in Docker for easier development)
echo -e "\n${YELLOW}Starting Backend...${NC}"
cd backend
./run_backend.sh &
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
echo -e "\n${YELLOW}Starting Frontend...${NC}"
cd ../dashboard
./run_frontend.sh

# Cleanup when done
echo -e "\n${YELLOW}Shutting down...${NC}"
kill $BACKEND_PID 2>/dev/null
docker-compose down