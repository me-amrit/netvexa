#!/bin/bash

echo "🚀 Setting up NETVEXA Marketing Site..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

# Create .env.local for local development
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
EOF
fi

echo "✅ Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  npm run dev"
echo ""
echo "The site will be available at:"
echo "  http://localhost:3000"
echo ""
echo "Available pages:"
echo "  - Homepage: http://localhost:3000"
echo "  - Blog: http://localhost:3000/blog"
echo "  - WordPress Integration: http://localhost:3000/integrations/wordpress"
echo "  - Compare vs Intercom: http://localhost:3000/compare/intercom-alternative"