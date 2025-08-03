# NETVEXA - AI Business Agent Platform

NETVEXA is an AI-powered business agent platform that enables SMEs to deploy intelligent conversational agents on their websites. Built with a production-grade RAG (Retrieval-Augmented Generation) pipeline, it provides context-aware customer support using your business knowledge.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for dashboard)
- At least one LLM API key:
  - **Google** (Gemini): [Get API key](https://makersuite.google.com/app/apikey) - Recommended
  - **Anthropic** (Claude): [Get API key](https://console.anthropic.com/)
  - **OpenAI** (GPT): [Get API key](https://platform.openai.com/)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/netvexa/netvexa.git
   cd netvexa
   ```

2. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys
   ```

3. **Start the platform**
   ```bash
   docker-compose up -d
   ```

4. **Start the dashboard** (in a new terminal)
   ```bash
   cd dashboard
   npm install
   npm start
   ```

5. **Access the application**
   - Dashboard: http://localhost:3001
   - API Docs: http://localhost:8000/docs
   - Backend Health: http://localhost:8000/health

## Project Structure

```
netvexa/
├── backend/              # FastAPI backend with RAG engine
├── dashboard/            # React TypeScript admin dashboard
├── homepage/             # Next.js public website
├── wordpress-plugin/     # WordPress integration (coming soon)
├── docs/                # Documentation
├── spec/                # Requirements and design specs
├── docker-compose.yml   # Docker services configuration
└── PROGRESS.md         # Development progress tracker
```

## ✨ Features

### Core Platform
- 🤖 **Multi-LLM Support**: Seamless integration with Google Gemini, OpenAI GPT, and Anthropic Claude
- 🔍 **Production RAG Pipeline**: Hybrid search combining vector similarity and BM25 keyword matching
- 💾 **Smart Caching**: Redis-powered caching for embeddings and responses
- 🐘 **PostgreSQL + pgvector**: Scalable vector storage with sub-100ms search
- 📚 **Knowledge Management**: Upload documents (PDF, TXT, MD), ingest URLs, or add text directly
- 🔐 **Enterprise Security**: JWT authentication, API keys, and role-based access control

### User Experience
- 💬 **Real-time Chat**: WebSocket-powered conversations with streaming responses
- 📊 **Analytics Dashboard**: Track usage, performance, and customer satisfaction
- 🎨 **Customizable Agents**: Configure personality, tone, and response style
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🔌 **Easy Integration**: Embeddable chat widget for any website

### Development
- 🚀 **Modern Stack**: FastAPI + React + TypeScript
- 🐳 **Docker Ready**: One-command deployment with Docker Compose
- 📖 **API Documentation**: Auto-generated OpenAPI/Swagger docs
- 🔄 **Hot Reload**: Development environment with live code updates
- 📝 **Comprehensive Logging**: Structured logs with rotation

## Configuration

### LLM Providers

Set your preferred provider in `.env`:
```env
LLM_PROVIDER=anthropic  # Options: anthropic, google, openai
```

### Model Selection

Configure specific models:
```env
ANTHROPIC_MODEL=claude-3-haiku-20240307
GOOGLE_MODEL=gemini-pro
OPENAI_MODEL=gpt-3.5-turbo
```

### Embedding Providers

```env
EMBEDDING_PROVIDER=google  # Options: google, openai
```

## Development

### Running Tests
```bash
cd backend
pytest
```

### Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Viewing Logs
```bash
docker-compose logs -f backend
```

## WordPress Plugin

1. Copy plugin to WordPress:
   ```bash
   cp -r wordpress-plugin/netvexa-chat /path/to/wordpress/wp-content/plugins/
   ```

2. Activate in WordPress admin

3. Configure with your API endpoint

## Production Deployment

See [Production Guide](docs/production-deployment.md) for AWS deployment instructions.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/netvexa/netvexa/issues)
- Email: support@netvexa.com

## License

Copyright (c) 2024 NETVEXA. All rights reserved.