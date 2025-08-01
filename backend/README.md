# NETVEXA MVP - Simple RAG Prototype

This is the MVP implementation of NETVEXA's AI-powered business agent with real-time chat capabilities.

## Features

- ✅ Real-time WebSocket chat interface
- ✅ Basic RAG (Retrieval Augmented Generation) using LlamaIndex
- ✅ Simple knowledge ingestion (text and URL)
- ✅ In-memory vector store for quick testing
- ✅ REST API fallback for non-WebSocket clients
- ✅ Simple web-based chat demo

## Quick Start

1. **Setup Environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Run the MVP**
   ```bash
   ./run_mvp.sh
   ```

3. **Access the Application**
   - Chat Demo: http://localhost:8000/static/index.html
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/

## API Endpoints

### Knowledge Management
- `POST /api/knowledge/ingest-text` - Ingest raw text
- `POST /api/knowledge/ingest-url` - Ingest content from URL

### Chat
- `WebSocket /ws/{agent_id}` - Real-time chat
- `POST /api/chat/message` - REST fallback

### Agent Configuration
- `GET /api/agents/{agent_id}/config` - Get agent configuration

## Testing the Chat

1. Open http://localhost:8000/static/index.html
2. The demo automatically ingests sample NETVEXA data
3. Try asking questions like:
   - "What is NETVEXA?"
   - "How much does it cost?"
   - "What are the key features?"
   - "How long does deployment take?"

## Architecture

- **FastAPI** - Modern Python web framework
- **LlamaIndex** - RAG orchestration
- **OpenAI** - LLM and embeddings
- **SQLite** - Simple database for MVP
- **WebSocket** - Real-time communication

## Next Steps

1. Add PostgreSQL with pgvector for production
2. Implement proper document chunking
3. Add Redis for conversation memory
4. Build WordPress plugin integration
5. Implement authentication and multi-tenancy