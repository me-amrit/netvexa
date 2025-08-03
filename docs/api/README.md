# NETVEXA API Documentation

## Overview

The NETVEXA API provides programmatic access to create and manage AI-powered customer support agents. This RESTful API supports both JSON and multipart form data for file uploads.

## Base URL

- **Production**: `https://api.netvexa.com/api`
- **Development**: `http://localhost:8000/api`

## Authentication

The API supports two authentication methods:

### 1. JWT Bearer Token (Dashboard Users)

For users accessing via the dashboard:

```bash
curl -X POST https://api.netvexa.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

Use the returned token in subsequent requests:

```bash
curl https://api.netvexa.com/api/agents \
  -H "Authorization: Bearer <jwt_token>"
```

### 2. API Key (Programmatic Access)

For server-to-server communication:

```bash
curl https://api.netvexa.com/api/agents \
  -H "X-API-Key: <your_api_key>"
```

## Quick Start

### 1. Create an Agent

```bash
curl -X POST https://api.netvexa.com/api/agents \
  -H "X-API-Key: <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Bot",
    "description": "Helps customers with product inquiries",
    "prompt": "You are a helpful customer support agent...",
    "model": "gpt-3.5-turbo",
    "welcome_message": "Hello! How can I help you today?"
  }'
```

### 2. Upload Knowledge Base

```bash
curl -X POST https://api.netvexa.com/api/knowledge/ingest/file \
  -H "X-API-Key: <your_api_key>" \
  -F "file=@/path/to/document.pdf" \
  -F "agent_id=<agent_id>" \
  -F "title=Product Manual"
```

### 3. Deploy Agent

```bash
curl -X POST https://api.netvexa.com/api/agents/<agent_id>/deploy \
  -H "X-API-Key: <your_api_key>"
```

## Rate Limiting

Rate limits are enforced based on your subscription tier:

| Tier | Requests/Hour |
|------|---------------|
| Starter | 100 |
| Growth | 1,000 |
| Professional | 5,000 |
| Business | Unlimited |

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

Configure webhooks to receive real-time updates:

```bash
curl -X POST https://api.netvexa.com/api/webhooks \
  -H "X-API-Key: <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["conversation.started", "lead.captured"],
    "secret": "your_webhook_secret"
  }'
```

### Webhook Events

- `conversation.started` - New chat conversation begins
- `conversation.message` - New message in conversation
- `conversation.resolved` - Conversation marked as resolved
- `lead.captured` - Email address collected
- `agent.trained` - Document processing completed

### Verifying Webhook Signatures

All webhooks include an HMAC signature in the `X-Netvexa-Signature` header:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

Error responses include details:

```json
{
  "error": "Invalid request",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
import { NetvexaClient } from '@netvexa/sdk';

const client = new NetvexaClient({
  apiKey: process.env.NETVEXA_API_KEY
});

// Create an agent
const agent = await client.agents.create({
  name: 'Support Bot',
  description: 'Customer support assistant',
  model: 'gpt-3.5-turbo'
});

// Upload knowledge
await client.knowledge.uploadFile(agent.id, {
  file: fileBuffer,
  title: 'Product Documentation'
});

// Get analytics
const analytics = await client.analytics.getAgentAnalytics(agent.id, {
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});
```

### Python

```python
from netvexa import NetvexaClient

client = NetvexaClient(api_key=os.environ['NETVEXA_API_KEY'])

# Create an agent
agent = client.agents.create(
    name='Support Bot',
    description='Customer support assistant',
    model='gpt-3.5-turbo'
)

# Upload knowledge
with open('docs.pdf', 'rb') as f:
    client.knowledge.upload_file(
        agent_id=agent.id,
        file=f,
        title='Product Documentation'
    )

# List conversations
conversations = client.conversations.list(
    agent_id=agent.id,
    status='active'
)
```

## API Client Libraries

Official SDKs are available for:

- JavaScript/TypeScript: `npm install @netvexa/sdk`
- Python: `pip install netvexa`
- PHP: `composer require netvexa/sdk`
- Ruby: `gem install netvexa`

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- [openapi.yaml](./openapi.yaml)
- [Swagger UI](https://api.netvexa.com/docs)

## Support

- Email: api-support@netvexa.com
- Documentation: https://docs.netvexa.com
- Status Page: https://status.netvexa.com