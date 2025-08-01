# NETVEXA - AI Business Agent Platform

NETVEXA is an AI-powered business agent platform that enables SMEs to deploy intelligent conversational agents on their websites within 1 hour.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- At least one API key:
  - **Anthropic** (Claude): [Get API key](https://console.anthropic.com/)
  - **Google** (Gemini): [Get API key](https://makersuite.google.com/app/apikey)
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
   # Edit backend/.env and add at least one API key
   ```

3. **Start development environment**
   ```bash
   ./start-dev.sh
   ```

4. **Access the application**
   - Chat Demo: http://localhost:8000/static/index.html
   - API Docs: http://localhost:8000/docs
   - pgAdmin: http://localhost:5050

## Project Structure

```
netvexa/
├── backend/              # FastAPI backend with RAG
├── wordpress-plugin/     # WordPress integration
├── docs/                # Documentation
├── spec/                # Requirements and design
└── docker-compose.yml   # Docker services
```

## Features

- 🤖 **Multi-LLM Support**: Anthropic Claude, Google Gemini, OpenAI GPT
- 🔄 **Automatic Fallback**: Seamless switching between providers
- 💾 **Smart Caching**: Redis-powered embedding cache
- 🐘 **PostgreSQL + pgvector**: Production-ready vector storage
- 🔌 **WordPress Plugin**: Easy integration for 43% of websites
- 💬 **Real-time Chat**: WebSocket-powered conversations

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