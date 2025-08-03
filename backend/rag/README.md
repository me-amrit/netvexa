# Production RAG System

This is the production-grade Retrieval-Augmented Generation (RAG) system for NETVEXA, featuring advanced document processing, hybrid search, and intelligent response generation.

## Features

### 1. Advanced Document Processing
- **Multiple Format Support**: PDF, DOCX, HTML, Markdown, Plain Text, Code files
- **Intelligent Chunking**: 
  - Semantic chunking for natural text
  - Section-aware chunking for structured documents
  - Code-aware chunking for source files
  - Configurable chunk size and overlap

### 2. Hybrid Search
- **Vector Search**: Semantic similarity using embeddings
- **Keyword Search**: BM25 scoring for exact matches
- **Combined Scoring**: Weighted combination of vector and keyword scores
- **Re-ranking**: Relevance-based re-ranking for better results

### 3. Production Features
- **Incremental Indexing**: Add documents without rebuilding entire index
- **Caching**: Redis-based caching for embeddings and conversations
- **Conversation History**: Maintains context across messages
- **Usage Tracking**: Integrated with billing system
- **Error Handling**: Graceful fallbacks and error recovery

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Document      │────▶│    Chunking      │────▶│   Embedding     │
│   Parsers       │     │   Strategies     │     │   Generation    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   LLM Response  │◀────│  Hybrid Search   │◀────│   PostgreSQL    │
│   Generation    │     │   & Re-ranking   │     │   + pgvector    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## API Endpoints

### Document Management

**Upload Document**
```bash
POST /api/knowledge/ingest/file
Content-Type: multipart/form-data

file: <binary>
agent_id: "agent_123"
metadata: {"category": "documentation"}
```

**Ingest Text**
```bash
POST /api/knowledge/ingest/text
Content-Type: application/json

{
  "text": "Your text content here",
  "agent_id": "agent_123",
  "title": "Document Title",
  "metadata": {"source": "manual"}
}
```

**Search Knowledge Base**
```bash
POST /api/knowledge/search
Content-Type: application/json

{
  "query": "How to integrate API?",
  "agent_id": "agent_123",
  "k": 5,
  "use_reranking": true
}
```

## Testing Interface

Run the interactive testing interface:

```bash
cd backend
python test_rag.py --interactive
```

Commands:
- `/ingest <file>` - Ingest a document
- `/search <query>` - Search knowledge base
- `/chat <message>` - Test chat with RAG
- `/stats` - Show statistics

## Configuration

Environment variables:
```env
# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=128

# Search
TOP_K_RETRIEVAL=5

# LLM Provider
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key

# Embedding Provider
EMBEDDING_PROVIDER=google
GOOGLE_API_KEY=your_key
```

## Document Chunking Strategies

### Semantic Chunking
Best for: Blog posts, articles, documentation
- Splits by paragraphs and semantic boundaries
- Maintains context within chunks

### Markdown Chunking
Best for: Technical documentation, README files
- Preserves section hierarchy
- Keeps code blocks intact

### Code Chunking
Best for: Source code files
- Chunks by functions/classes
- Preserves syntax integrity

### Sentence Chunking
Best for: Short texts, FAQs
- Splits by sentences
- Respects chunk size limits

## Search Scoring

The hybrid search combines:
1. **Vector Score** (70% weight): Semantic similarity
2. **Keyword Score** (30% weight): BM25 relevance

Re-ranking considers:
- Query coverage
- Position of matches
- Document freshness
- Length penalties

## Performance Optimization

1. **Batch Processing**: Documents processed in batches of 10
2. **Async Operations**: All I/O operations are asynchronous
3. **Caching**: Embeddings cached in Redis
4. **Incremental Updates**: Only new documents are processed

## Usage Limits

Based on subscription tier:
- **Starter**: 2,000 messages/month
- **Growth**: 8,000 messages/month
- **Professional**: 25,000 messages/month
- **Business**: 60,000 messages/month

## Troubleshooting

### Common Issues

1. **PDF parsing fails**
   - Ensure `pypdf` is installed
   - Check if PDF is not corrupted
   - Try re-saving PDF with different tool

2. **Embeddings not generated**
   - Verify API keys are set
   - Check embedding provider limits
   - Review logs for API errors

3. **Search returns no results**
   - Ensure documents are ingested
   - Check agent_id matches
   - Verify embeddings were generated

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('backend.rag').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Cross-encoder Re-ranking**: Better relevance scoring
2. **Multi-modal Support**: Images and tables
3. **Streaming Responses**: Real-time generation
4. **Custom Embeddings**: Fine-tuned models
5. **Query Expansion**: Automatic query enhancement