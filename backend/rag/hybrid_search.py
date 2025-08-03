"""
Hybrid search combining vector similarity and keyword matching
"""
import re
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from collections import Counter
import logging
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from database import KnowledgeDocument, get_db

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Container for search results"""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    vector_score: float
    keyword_score: float
    combined_score: float
    highlights: List[str]


class HybridSearchEngine:
    """Combines vector similarity and keyword search for better retrieval"""
    
    def __init__(self, 
                 vector_weight: float = 0.7,
                 keyword_weight: float = 0.3,
                 use_bm25: bool = True):
        """
        Initialize hybrid search engine
        
        Args:
            vector_weight: Weight for vector similarity score (0-1)
            keyword_weight: Weight for keyword score (0-1)
            use_bm25: Use BM25 scoring for keywords instead of TF-IDF
        """
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        self.use_bm25 = use_bm25
        
        # Ensure weights sum to 1
        total_weight = vector_weight + keyword_weight
        if total_weight != 1.0:
            self.vector_weight = vector_weight / total_weight
            self.keyword_weight = keyword_weight / total_weight
    
    async def search(self,
                    query: str,
                    query_embedding: List[float],
                    agent_id: str,
                    k: int = 10,
                    keyword_k: int = 20,
                    db: AsyncSession = None,
                    filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Perform hybrid search combining vector and keyword search
        
        Args:
            query: Search query text
            query_embedding: Query embedding vector
            agent_id: Agent ID to search within
            k: Number of results to return
            keyword_k: Number of keyword results to fetch before reranking
            db: Database session
            filters: Additional filters to apply
        
        Returns:
            List of SearchResult objects sorted by combined score
        """
        # Perform vector search
        vector_results = await self._vector_search(
            query_embedding, agent_id, k * 2, db, filters
        )
        
        # Perform keyword search
        keyword_results = await self._keyword_search(
            query, agent_id, keyword_k, db, filters
        )
        
        # Combine and rerank results
        combined_results = self._combine_results(
            vector_results, keyword_results, query
        )
        
        # Sort by combined score and return top k
        combined_results.sort(key=lambda x: x.combined_score, reverse=True)
        return combined_results[:k]
    
    async def _vector_search(self,
                           query_embedding: List[float],
                           agent_id: str,
                           k: int,
                           db: AsyncSession,
                           filters: Optional[Dict[str, Any]] = None) -> List[Tuple[KnowledgeDocument, float]]:
        """Perform vector similarity search"""
        try:
            # Convert embedding to proper format for pgvector
            from pgvector.sqlalchemy import Vector
            
            # Base query - use the <-> operator for cosine distance
            query = select(
                KnowledgeDocument,
                KnowledgeDocument.embedding.cosine_distance(query_embedding).label('distance')
            ).where(
                and_(
                    KnowledgeDocument.agent_id == agent_id,
                    KnowledgeDocument.embedding.isnot(None)
                )
            )
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(KnowledgeDocument, key):
                        query = query.where(
                            getattr(KnowledgeDocument, key) == value
                        )
            
            # Order by similarity and limit
            query = query.order_by('distance').limit(k)
            
            # Execute query
            result = await db.execute(query)
            documents = result.all()
            
            # Convert distance to similarity score (1 - distance for cosine)
            return [(doc, 1 - distance) for doc, distance in documents]
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    async def _keyword_search(self,
                            query: str,
                            agent_id: str,
                            k: int,
                            db: AsyncSession,
                            filters: Optional[Dict[str, Any]] = None) -> List[Tuple[KnowledgeDocument, float]]:
        """Perform keyword-based search"""
        try:
            # Tokenize query
            query_tokens = self._tokenize(query.lower())
            
            if not query_tokens:
                return []
            
            # Build search conditions
            search_conditions = []
            for token in query_tokens:
                search_conditions.append(
                    func.lower(KnowledgeDocument.content).contains(token)
                )
            
            # Base query
            query_obj = select(KnowledgeDocument).where(
                and_(
                    KnowledgeDocument.agent_id == agent_id,
                    or_(*search_conditions)  # Match any token
                )
            )
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(KnowledgeDocument, key):
                        query_obj = query_obj.where(
                            getattr(KnowledgeDocument, key) == value
                        )
            
            # Execute query
            result = await db.execute(query_obj.limit(k))
            documents = result.scalars().all()
            
            # Score documents
            scored_documents = []
            for doc in documents:
                if self.use_bm25:
                    score = self._calculate_bm25_score(
                        doc.content, query_tokens, documents
                    )
                else:
                    score = self._calculate_tfidf_score(
                        doc.content, query_tokens
                    )
                scored_documents.append((doc, score))
            
            # Sort by score
            scored_documents.sort(key=lambda x: x[1], reverse=True)
            return scored_documents
            
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Remove special characters and split
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.lower().split()
        
        # Remove stop words (basic list)
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or',
            'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that',
            'this', 'it', 'from', 'be', 'are', 'been', 'was', 'were'
        }
        
        return [token for token in tokens if token not in stop_words and len(token) > 2]
    
    def _calculate_tfidf_score(self, content: str, query_tokens: List[str]) -> float:
        """Calculate TF-IDF score for document"""
        content_lower = content.lower()
        content_tokens = self._tokenize(content_lower)
        
        if not content_tokens:
            return 0.0
        
        # Calculate term frequency
        tf_scores = []
        for token in query_tokens:
            tf = content_tokens.count(token) / len(content_tokens)
            tf_scores.append(tf)
        
        # Simple IDF (would need corpus statistics for proper IDF)
        # Using log(1 + 1/tf) as a simple approximation
        score = 0.0
        for tf in tf_scores:
            if tf > 0:
                idf = math.log(1 + 1/tf)
                score += tf * idf
        
        return score
    
    def _calculate_bm25_score(self, 
                            content: str, 
                            query_tokens: List[str],
                            all_documents: List[KnowledgeDocument],
                            k1: float = 1.2,
                            b: float = 0.75) -> float:
        """Calculate BM25 score for document"""
        content_lower = content.lower()
        content_tokens = self._tokenize(content_lower)
        
        if not content_tokens:
            return 0.0
        
        # Calculate average document length
        avg_doc_length = np.mean([
            len(self._tokenize(doc.content)) for doc in all_documents
        ])
        
        doc_length = len(content_tokens)
        
        score = 0.0
        for token in query_tokens:
            # Term frequency in document
            tf = content_tokens.count(token)
            
            if tf == 0:
                continue
            
            # Document frequency (how many documents contain the term)
            df = sum(1 for doc in all_documents if token in doc.content.lower())
            
            # IDF calculation
            N = len(all_documents)
            idf = math.log((N - df + 0.5) / (df + 0.5))
            
            # BM25 formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def _combine_results(self,
                        vector_results: List[Tuple[KnowledgeDocument, float]],
                        keyword_results: List[Tuple[KnowledgeDocument, float]],
                        query: str) -> List[SearchResult]:
        """Combine vector and keyword search results"""
        # Create dictionaries for easy lookup
        vector_scores = {doc.id: score for doc, score in vector_results}
        keyword_scores = {doc.id: score for doc, score in keyword_results}
        
        # Get all unique documents
        all_docs = {}
        for doc, _ in vector_results + keyword_results:
            all_docs[doc.id] = doc
        
        # Normalize scores
        max_vector_score = max(vector_scores.values()) if vector_scores else 1.0
        max_keyword_score = max(keyword_scores.values()) if keyword_scores else 1.0
        
        # Combine scores
        results = []
        for doc_id, doc in all_docs.items():
            # Get normalized scores
            vector_score = vector_scores.get(doc_id, 0.0) / max_vector_score
            keyword_score = keyword_scores.get(doc_id, 0.0) / max_keyword_score
            
            # Calculate combined score
            combined_score = (
                self.vector_weight * vector_score +
                self.keyword_weight * keyword_score
            )
            
            # Extract highlights
            highlights = self._extract_highlights(doc.content, query)
            
            results.append(SearchResult(
                document_id=doc.id,
                content=doc.content,
                metadata=doc.meta_data or {},
                vector_score=vector_score,
                keyword_score=keyword_score,
                combined_score=combined_score,
                highlights=highlights
            ))
        
        return results
    
    def _extract_highlights(self, content: str, query: str, 
                          context_words: int = 10) -> List[str]:
        """Extract relevant snippets from content"""
        highlights = []
        query_tokens = self._tokenize(query.lower())
        content_lower = content.lower()
        
        for token in query_tokens:
            # Find all occurrences of the token
            start = 0
            while True:
                pos = content_lower.find(token, start)
                if pos == -1:
                    break
                
                # Extract context around the match
                words = content.split()
                word_positions = []
                current_pos = 0
                
                for i, word in enumerate(words):
                    word_positions.append((current_pos, current_pos + len(word)))
                    current_pos += len(word) + 1
                
                # Find which word contains our match
                match_word_idx = None
                for i, (start_pos, end_pos) in enumerate(word_positions):
                    if start_pos <= pos <= end_pos:
                        match_word_idx = i
                        break
                
                if match_word_idx is not None:
                    # Extract context
                    start_idx = max(0, match_word_idx - context_words)
                    end_idx = min(len(words), match_word_idx + context_words + 1)
                    
                    highlight = ' '.join(words[start_idx:end_idx])
                    
                    # Add ellipsis if needed
                    if start_idx > 0:
                        highlight = '...' + highlight
                    if end_idx < len(words):
                        highlight = highlight + '...'
                    
                    highlights.append(highlight)
                
                start = pos + 1
                
                # Limit number of highlights per token
                if len(highlights) >= 3:
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_highlights = []
        for highlight in highlights:
            if highlight not in seen:
                seen.add(highlight)
                unique_highlights.append(highlight)
        
        return unique_highlights[:5]  # Return top 5 highlights


class ReRanker:
    """Re-ranking module for search results"""
    
    def __init__(self, use_cross_encoder: bool = False):
        """
        Initialize re-ranker
        
        Args:
            use_cross_encoder: Use cross-encoder model for re-ranking
        """
        self.use_cross_encoder = use_cross_encoder
        
        if use_cross_encoder:
            # In production, load a cross-encoder model
            # For now, we'll use a simple implementation
            logger.info("Cross-encoder re-ranking not fully implemented")
    
    async def rerank(self, 
                    query: str,
                    results: List[SearchResult],
                    top_k: int = None) -> List[SearchResult]:
        """
        Re-rank search results for better relevance
        
        Args:
            query: Original search query
            results: List of search results to re-rank
            top_k: Number of results to return (None for all)
        
        Returns:
            Re-ranked list of search results
        """
        if self.use_cross_encoder:
            # In production, use cross-encoder model
            # For now, use relevance scoring
            return await self._relevance_rerank(query, results, top_k)
        else:
            # Use feature-based re-ranking
            return self._feature_rerank(query, results, top_k)
    
    async def _relevance_rerank(self, 
                              query: str,
                              results: List[SearchResult],
                              top_k: int = None) -> List[SearchResult]:
        """Re-rank using relevance scoring"""
        # Calculate relevance scores
        for result in results:
            relevance_score = self._calculate_relevance(query, result.content)
            # Adjust combined score with relevance
            result.combined_score = (
                0.7 * result.combined_score + 
                0.3 * relevance_score
            )
        
        # Sort by new combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)
        
        return results[:top_k] if top_k else results
    
    def _feature_rerank(self, 
                       query: str,
                       results: List[SearchResult],
                       top_k: int = None) -> List[SearchResult]:
        """Re-rank using multiple features"""
        query_tokens = set(self._tokenize(query.lower()))
        
        for result in results:
            # Calculate various features
            features = {
                'exact_match': self._has_exact_match(query, result.content),
                'query_coverage': self._calculate_query_coverage(
                    query_tokens, result.content
                ),
                'position_score': self._calculate_position_score(
                    query_tokens, result.content
                ),
                'length_penalty': self._calculate_length_penalty(result.content),
                'freshness': self._calculate_freshness(result.metadata)
            }
            
            # Combine features into final score
            feature_score = (
                0.3 * features['exact_match'] +
                0.2 * features['query_coverage'] +
                0.2 * features['position_score'] +
                0.1 * features['length_penalty'] +
                0.2 * features['freshness']
            )
            
            # Adjust combined score
            result.combined_score = (
                0.6 * result.combined_score + 
                0.4 * feature_score
            )
        
        # Sort by new combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)
        
        return results[:top_k] if top_k else results
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text (reuse from HybridSearchEngine)"""
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.lower().split()
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or',
            'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that',
            'this', 'it', 'from', 'be', 'are', 'been', 'was', 'were'
        }
        return [token for token in tokens if token not in stop_words and len(token) > 2]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate semantic relevance score"""
        # Simple implementation - in production, use a model
        query_tokens = set(self._tokenize(query.lower()))
        content_tokens = set(self._tokenize(content.lower()))
        
        if not query_tokens:
            return 0.0
        
        # Jaccard similarity
        intersection = query_tokens.intersection(content_tokens)
        union = query_tokens.union(content_tokens)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _has_exact_match(self, query: str, content: str) -> float:
        """Check if content contains exact query match"""
        return 1.0 if query.lower() in content.lower() else 0.0
    
    def _calculate_query_coverage(self, query_tokens: set, content: str) -> float:
        """Calculate what percentage of query tokens appear in content"""
        if not query_tokens:
            return 0.0
        
        content_lower = content.lower()
        found_tokens = sum(1 for token in query_tokens if token in content_lower)
        
        return found_tokens / len(query_tokens)
    
    def _calculate_position_score(self, query_tokens: set, content: str) -> float:
        """Score based on position of query tokens in content"""
        content_lower = content.lower()
        
        if not query_tokens:
            return 0.0
        
        # Find earliest position of any query token
        min_position = len(content)
        for token in query_tokens:
            pos = content_lower.find(token)
            if pos != -1 and pos < min_position:
                min_position = pos
        
        # Convert to score (earlier = better)
        if min_position == len(content):
            return 0.0
        else:
            return 1.0 - (min_position / len(content))
    
    def _calculate_length_penalty(self, content: str) -> float:
        """Penalize very short or very long documents"""
        length = len(content)
        
        if length < 50:
            return 0.5  # Too short
        elif length > 5000:
            return 0.7  # Too long
        else:
            return 1.0  # Just right
    
    def _calculate_freshness(self, metadata: Dict[str, Any]) -> float:
        """Score based on document freshness"""
        # Check if we have a timestamp
        created_at = metadata.get('created_at')
        if not created_at:
            return 0.5  # Neutral score if no timestamp
        
        # In production, calculate based on age
        # For now, return neutral score
        return 0.5