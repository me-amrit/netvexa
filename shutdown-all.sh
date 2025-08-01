#!/bin/bash

echo "🛑 Shutting down NETVEXA services..."
echo ""

# Function to check if a process is running
check_process() {
    if ps aux | grep -v grep | grep -q "$1"; then
        return 0
    else
        return 1
    fi
}

# Shutdown Docker containers
echo "📦 Stopping Docker containers..."
if command -v docker-compose &> /dev/null; then
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        echo "✅ Docker containers stopped"
    else
        echo "ℹ️  No Docker containers running"
    fi
else
    echo "⚠️  docker-compose not found, skipping Docker shutdown"
fi

# Find and kill Next.js development server
echo ""
echo "🌐 Stopping marketing website..."

# Find Next.js process
NEXT_PID=$(ps aux | grep "next dev" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$NEXT_PID" ]; then
    echo "Found Next.js process (PID: $NEXT_PID)"
    kill $NEXT_PID
    echo "✅ Marketing site stopped"
else
    echo "ℹ️  Marketing site not running"
fi

# Clean up any orphaned node processes in marketing-site
echo ""
echo "🧹 Cleaning up orphaned processes..."

# Kill any node processes related to the marketing site
ps aux | grep "marketing-site.*node" | grep -v grep | awk '{print $2}' | while read pid; do
    echo "Killing orphaned process: $pid"
    kill $pid 2>/dev/null
done

# Optional: Remove Next.js cache
echo ""
echo "🗑️  Cleaning up cache files..."
if [ -d "/Users/amrit/Repo/netvexa/marketing-site/.next" ]; then
    rm -rf /Users/amrit/Repo/netvexa/marketing-site/.next
    echo "✅ Next.js cache cleared"
fi

# Remove log files
if [ -f "/Users/amrit/Repo/netvexa/marketing-site/dev.log" ]; then
    rm /Users/amrit/Repo/netvexa/marketing-site/dev.log
    echo "✅ Log files removed"
fi

echo ""
echo "✅ All services shut down successfully!"
echo ""
echo "To restart services:"
echo "  - Backend: ./start-dev.sh"
echo "  - Marketing: cd marketing-site && ./start-dev.sh"