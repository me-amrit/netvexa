#!/bin/bash

echo "🚀 Starting NETVEXA MVP..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please update .env with your OpenAI API key before continuing."
    echo "   Edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Please update your OPENAI_API_KEY in .env file"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Starting FastAPI server..."
echo "📍 API: http://localhost:8000"
echo "💬 Chat Demo: http://localhost:8000/static/index.html"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""

python main.py