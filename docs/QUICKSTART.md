# NETVEXA Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Docker Desktop installed and running
- Node.js 18+ installed
- A Google Gemini API key (free tier available)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/netvexa/netvexa.git
cd netvexa

# Copy environment template
cp backend/.env.example backend/.env
```

### Step 2: Add Your API Key

Edit `backend/.env` and add your Google API key:
```env
GOOGLE_API_KEY=your-api-key-here
LLM_PROVIDER=google
EMBEDDING_PROVIDER=google
```

### Step 3: Start the Platform

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)
docker-compose ps

# Start the dashboard (in a new terminal)
cd dashboard
npm install
npm start
```

### Step 4: Access NETVEXA

- **Dashboard**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 5: Create Your First Agent

1. Open the dashboard at http://localhost:3001
2. Register a new account or login
3. Click "Create Agent"
4. Give your agent a name (e.g., "Customer Support Bot")
5. Click "Save"

### Step 6: Upload Knowledge

1. Click on your agent
2. Go to the "Documents" tab
3. Click "Upload Document"
4. Upload a text file, PDF, or markdown file
5. Wait for processing to complete

### Step 7: Test Your Agent

1. Go to the "Test Chat" tab
2. Type a question related to your uploaded document
3. See your agent respond with context-aware answers!

## 🛠️ Common Commands

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend
```

### Restart Services
```bash
docker-compose restart backend
```

### Stop Everything
```bash
docker-compose down
```

## 🔧 Troubleshooting

### Backend Not Starting?
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Invalid API key: Check your .env file
# - Port conflict: Ensure ports 8000, 5432, 6379 are free
```

### Can't Access Dashboard?
```bash
# Ensure npm install completed
cd dashboard
npm install

# Check for errors
npm start
```

### Database Issues?
```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
```

## 📚 Next Steps

1. **Read the Docs**
   - [Architecture Overview](./how-netvexa-works.md)
   - [API Documentation](http://localhost:8000/docs)
   - [Progress Report](../PROGRESS.md)

2. **Customize Your Agent**
   - Edit personality settings
   - Add custom welcome messages
   - Configure response styles

3. **Integrate with Your Website**
   - Get your API key from the dashboard
   - Embed the chat widget
   - Monitor conversations

## 🆘 Need Help?

- Check [PROGRESS.md](../PROGRESS.md) for current status
- Review [tasks-updated.md](../spec/tasks-updated.md) for roadmap
- Open an issue on GitHub
- Contact: support@netvexa.com

## 🎯 Quick Tips

1. **Better Responses**: Upload multiple related documents for comprehensive knowledge
2. **Performance**: Documents are automatically chunked and indexed for fast retrieval
3. **Testing**: Use the test chat to refine your agent's responses before deployment
4. **Monitoring**: Check the logs for detailed information about queries and responses

Happy building! 🚀