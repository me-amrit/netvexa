#!/bin/bash

echo "🚀 Starting NETVEXA Development Environment..."

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your API keys:"
    echo "   - ANTHROPIC_API_KEY (for Claude)"
    echo "   - GOOGLE_API_KEY (for Gemini)"
    echo "   - OPENAI_API_KEY (for GPT)"
    echo ""
    echo "You need at least ONE API key to continue."
    exit 1
fi

# Check if all API keys still have placeholder values
ANTHROPIC_SET=false
GOOGLE_SET=false
OPENAI_SET=false

if ! grep -q "ANTHROPIC_API_KEY=your_anthropic_api_key_here" backend/.env && grep -q "ANTHROPIC_API_KEY=" backend/.env; then
    ANTHROPIC_SET=true
fi
if ! grep -q "GOOGLE_API_KEY=your_google_api_key_here" backend/.env && grep -q "GOOGLE_API_KEY=" backend/.env; then
    GOOGLE_SET=true
fi
if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" backend/.env && grep -q "OPENAI_API_KEY=" backend/.env; then
    OPENAI_SET=true
fi

# Check if at least one API key is properly set
if [ "$ANTHROPIC_SET" = false ] && [ "$GOOGLE_SET" = false ] && [ "$OPENAI_SET" = false ]; then
    echo "❌ Please update at least one API key in backend/.env"
    echo "   Supported providers:"
    echo "   - Anthropic (Claude): ANTHROPIC_API_KEY"
    echo "   - Google (Gemini): GOOGLE_API_KEY"
    echo "   - OpenAI (GPT): OPENAI_API_KEY"
    exit 1
fi

# Detect which API keys are configured
echo "🔍 Checking configured providers..."
PROVIDERS=""
if [ "$ANTHROPIC_SET" = true ]; then
    PROVIDERS="$PROVIDERS Anthropic"
fi
if [ "$GOOGLE_SET" = true ]; then
    PROVIDERS="$PROVIDERS Google"
fi
if [ "$OPENAI_SET" = true ]; then
    PROVIDERS="$PROVIDERS OpenAI"
fi
echo "✅ Available providers:$PROVIDERS"

# Export environment variables for Docker Compose
echo "📋 Loading environment variables..."
set -a
source backend/.env
set +a

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

if ! docker-compose ps | grep -q "redis.*Up"; then
    echo "❌ Redis failed to start"
    exit 1
fi

echo "✅ Services are ready!"

# Run backend in development mode
echo "🔧 Starting backend development server..."
echo ""
echo "📍 Services:"
echo "   - API: http://localhost:8000"
echo "   - Chat Demo: http://localhost:8000/static/index.html"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - pgAdmin: http://localhost:5050 (admin@netvexa.com / admin)"
echo ""
echo "💡 Tips:"
echo "   - The backend will auto-reload on code changes"
echo "   - Check logs: docker-compose logs -f backend"
echo "   - Stop all: docker-compose down"
echo ""

# Start the backend with environment variables
export GOOGLE_API_KEY
export ANTHROPIC_API_KEY
export OPENAI_API_KEY
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up backend