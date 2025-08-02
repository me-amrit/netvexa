#!/bin/bash

echo "Starting NETVEXA Dashboard Setup..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install npm."
    exit 1
fi

echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"

# Install dependencies
echo "Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
EOL
fi

# Build CSS with Tailwind
echo "Building Tailwind CSS..."
npm run build:css 2>/dev/null || echo "No Tailwind build script found, using default"

# Start the development server
echo "Starting dashboard on http://localhost:3000..."
echo "Make sure the backend is running on http://localhost:8000"
npm start