#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 Starting NETVEXA Home Page${NC}"
echo "================================"

# Check if homepage directory exists
if [ ! -d "homepage" ]; then
    echo -e "${RED}Error: homepage directory not found${NC}"
    echo "Please run this script from the NETVEXA root directory"
    exit 1
fi

# Change to homepage directory
cd homepage

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    echo "This may take a few minutes on first run..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Set default port for homepage (3001 to avoid conflict with dashboard on 3000)
export PORT=3001

# Check if port 3001 is already in use
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
    
    # Check what's using the port
    PROCESS_INFO=$(lsof -ti:$PORT | xargs ps -p | tail -n 1)
    echo -e "${YELLOW}Process using port $PORT: $PROCESS_INFO${NC}"
    
    echo ""
    echo "Would you like to:"
    echo "1) Kill the process and use port $PORT"
    echo "2) Use a different port"
    echo "3) Cancel"
    read -p "Choose (1-3): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Stopping process on port $PORT...${NC}"
            lsof -ti:$PORT | xargs kill -9
            sleep 2
            ;;
        2)
            read -p "Enter port number (e.g., 3002): " NEW_PORT
            export PORT=$NEW_PORT
            echo -e "${BLUE}Using port $PORT instead${NC}"
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
echo ""
echo -e "${GREEN}🚀 Starting Next.js development server...${NC}"
echo ""
echo -e "${BLUE}📍 Access the home page at:${NC}"
echo -e "  ${GREEN}http://localhost:${PORT}${NC}"
echo ""
echo -e "${BLUE}📄 Available Pages:${NC}"
echo -e "  Homepage:      ${GREEN}http://localhost:${PORT}${NC}"
echo -e "  Blog:          ${GREEN}http://localhost:${PORT}/blog${NC}"
echo -e "  WordPress:     ${GREEN}http://localhost:${PORT}/integrations/wordpress${NC}"
echo -e "  Comparisons:   ${GREEN}http://localhost:${PORT}/compare/intercom-alternative${NC}"
echo ""
echo -e "${YELLOW}💡 Development Tips:${NC}"
echo "  • The server will auto-reload when you edit files"
echo "  • Press Ctrl+C to stop the server"
echo "  • Edit pages in: homepage/pages/"
echo "  • Edit components in: homepage/components/"
echo "  • Edit styles in: homepage/styles/globals.css"
echo ""
echo -e "${BLUE}🔧 To test UI changes:${NC}"
echo "  • Open the file you want to edit"
echo "  • Make your changes"
echo "  • Save the file"
echo "  • The browser will auto-refresh!"
echo ""

# Run the development server
npm run dev