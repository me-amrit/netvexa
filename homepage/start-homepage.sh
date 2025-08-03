#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 Starting NETVEXA Home Page${NC}"
echo "================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found${NC}"
    echo "Please run this script from the marketing-site directory"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Set default port for homepage (3001 to avoid conflict with dashboard on 3000)
export PORT=3001

# Check if port 3001 is already in use
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
    echo "Would you like to:"
    echo "1) Kill the process using port $PORT"
    echo "2) Use a different port"
    echo "3) Cancel"
    read -p "Choose (1-3): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Killing process on port $PORT...${NC}"
            lsof -ti:$PORT | xargs kill -9
            sleep 1
            ;;
        2)
            read -p "Enter port number (e.g., 3002): " NEW_PORT
            export PORT=$NEW_PORT
            echo -e "${BLUE}Using port $PORT${NC}"
            ;;
        3)
            echo -e "${YELLOW}Cancelled${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

# Start the development server
echo -e "${GREEN}🚀 Starting Next.js development server on port $PORT...${NC}"
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo -e "  Homepage:      ${GREEN}http://localhost:${PORT}${NC}"
echo -e "  Blog:          ${GREEN}http://localhost:${PORT}/blog${NC}"
echo -e "  WordPress:     ${GREEN}http://localhost:${PORT}/integrations/wordpress${NC}"
echo -e "  Comparisons:   ${GREEN}http://localhost:${PORT}/compare/intercom-alternative${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  - The server will auto-reload on file changes"
echo "  - Press Ctrl+C to stop the server"
echo "  - Edit pages in the 'pages' directory"
echo "  - Edit components in the 'components' directory"
echo ""

# Run the development server
npm run dev