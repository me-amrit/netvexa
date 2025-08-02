#!/bin/bash

echo "Starting NETVEXA Backend Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
DATABASE_URL=postgresql://postgres:netvexa_password@localhost:5433/netvexa_db
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
OPENAI_API_KEY=your-openai-api-key-here
STRIPE_API_KEY=your-stripe-api-key-here
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret-here
EOL
    echo "Please update the .env file with your actual API keys"
fi

# Check if PostgreSQL is running (Docker or local)
if pg_isready -h localhost -p 5433 > /dev/null 2>&1; then
    echo "PostgreSQL (Docker) is running on port 5433"
elif pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL (local) is running on port 5432"
    echo "Note: The .env file is configured for Docker PostgreSQL on port 5433"
else
    echo "PostgreSQL is not running. Please ensure Docker containers are running:"
    echo "Run: docker-compose up -d postgres"
    exit 1
fi

# Run database migrations
echo "Running database setup..."
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"

# Start the backend server
echo "Starting backend server on http://localhost:8000..."
echo "API documentation will be available at http://localhost:8000/docs"
uvicorn main:app --reload --host 0.0.0.0 --port 8000