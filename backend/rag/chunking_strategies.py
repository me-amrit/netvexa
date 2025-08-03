"""
Advanced chunking strategies for production RAG
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import tiktoken
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except:
    pass


@dataclass
class ChunkMetadata:
    """Metadata for each chunk"""
    chunk_id: str
    chunk_index: int
    start_char: int
    end_char: int
    word_count: int
    token_count: int
    has_code: bool
    language: Optional[str] = None
    section_title: Optional[str] = None
    page_number: Optional[int] = None


class ChunkingStrategy:
    """Base class for chunking strategies"""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 chunk_overlap: int = 128,
                 min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk text and return chunks with metadata"""
        raise NotImplementedError


class SentenceChunker(ChunkingStrategy):
    """Chunks text by sentences, respecting chunk size limits"""
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk text by sentences"""
        chunks = []
        sentences = sent_tokenize(text)
        
        current_chunk = []
        current_tokens = 0
        current_start = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence exceeds chunk size, split it
            if sentence_tokens > self.chunk_size:
                # Finish current chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, current_start, metadata
                    ))
                    chunk_index += 1
                
                # Split large sentence
                words = sentence.split()
                word_chunks = []
                current_word_chunk = []
                current_word_tokens = 0
                
                for word in words:
                    word_tokens = self.count_tokens(word + ' ')
                    if current_word_tokens + word_tokens > self.chunk_size:
                        if current_word_chunk:
                            word_chunks.append(' '.join(current_word_chunk))
                            current_word_chunk = [word]
                            current_word_tokens = word_tokens
                    else:
                        current_word_chunk.append(word)
                        current_word_tokens += word_tokens
                
                if current_word_chunk:
                    word_chunks.append(' '.join(current_word_chunk))
                
                # Add word chunks
                for word_chunk in word_chunks:
                    chunks.append(self._create_chunk(
                        word_chunk, chunk_index, current_start, metadata
                    ))
                    chunk_index += 1
                    current_start += len(word_chunk) + 1
                
                current_chunk = []
                current_tokens = 0
                continue
            
            # Check if adding sentence exceeds chunk size
            if current_tokens + sentence_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, current_start, metadata
                    ))
                    chunk_index += 1
                
                # Handle overlap
                if self.chunk_overlap > 0 and chunks:
                    overlap_sentences = []
                    overlap_tokens = 0
                    
                    # Go back through sentences for overlap
                    for j in range(len(current_chunk) - 1, -1, -1):
                        sent = current_chunk[j]
                        sent_tokens = self.count_tokens(sent)
                        if overlap_tokens + sent_tokens <= self.chunk_overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_tokens += sent_tokens
                        else:
                            break
                    
                    current_chunk = overlap_sentences + [sentence]
                    current_tokens = overlap_tokens + sentence_tokens
                else:
                    current_chunk = [sentence]
                    current_tokens = sentence_tokens
                    current_start += len(chunk_text) + 1
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if self.count_tokens(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(
                    chunk_text, chunk_index, current_start, metadata
                ))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, start: int, metadata: Dict) -> Tuple[str, ChunkMetadata]:
        """Create chunk with metadata"""
        import uuid
        
        chunk_metadata = ChunkMetadata(
            chunk_id=str(uuid.uuid4()),
            chunk_index=index,
            start_char=start,
            end_char=start + len(text),
            word_count=len(text.split()),
            token_count=self.count_tokens(text),
            has_code=bool(re.search(r'```|def |class |function |import |from ', text)),
            section_title=metadata.get('section_title') if metadata else None,
            page_number=metadata.get('page_number') if metadata else None
        )
        
        return text, chunk_metadata


class SemanticChunker(ChunkingStrategy):
    """Chunks text based on semantic boundaries (paragraphs, sections)"""
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk text by semantic boundaries"""
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = []
        current_tokens = 0
        current_start = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            para_tokens = self.count_tokens(paragraph)
            
            # If paragraph exceeds chunk size, use sentence chunker
            if para_tokens > self.chunk_size:
                # Save current chunk first
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, current_start, metadata
                    ))
                    chunk_index += 1
                    current_start += len(chunk_text) + 2
                
                # Use sentence chunker for large paragraph
                sentence_chunker = SentenceChunker(
                    self.chunk_size, self.chunk_overlap, self.min_chunk_size
                )
                para_chunks = sentence_chunker.chunk(paragraph, metadata)
                
                for para_chunk_text, para_chunk_meta in para_chunks:
                    para_chunk_meta.chunk_index = chunk_index
                    chunks.append((para_chunk_text, para_chunk_meta))
                    chunk_index += 1
                
                current_chunk = []
                current_tokens = 0
                continue
            
            # Check if adding paragraph exceeds chunk size
            if current_tokens + para_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, current_start, metadata
                    ))
                    chunk_index += 1
                    current_start += len(chunk_text) + 2
                
                current_chunk = [paragraph]
                current_tokens = para_tokens
            else:
                current_chunk.append(paragraph)
                current_tokens += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if self.count_tokens(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(
                    chunk_text, chunk_index, current_start, metadata
                ))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, start: int, metadata: Dict) -> Tuple[str, ChunkMetadata]:
        """Create chunk with metadata"""
        import uuid
        
        chunk_metadata = ChunkMetadata(
            chunk_id=str(uuid.uuid4()),
            chunk_index=index,
            start_char=start,
            end_char=start + len(text),
            word_count=len(text.split()),
            token_count=self.count_tokens(text),
            has_code=bool(re.search(r'```|def |class |function |import |from ', text)),
            section_title=metadata.get('section_title') if metadata else None,
            page_number=metadata.get('page_number') if metadata else None
        )
        
        return text, chunk_metadata


class MarkdownChunker(ChunkingStrategy):
    """Specialized chunker for Markdown documents"""
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk markdown by sections and code blocks"""
        chunks = []
        
        # Extract code blocks first to preserve them
        code_blocks = []
        code_pattern = r'```[\s\S]*?```'
        
        def replace_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        text_no_code = re.sub(code_pattern, replace_code, text)
        
        # Split by headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        sections = []
        current_section = {'title': None, 'level': 0, 'content': []}
        
        for line in text_no_code.split('\n'):
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section
                if current_section['content']:
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                current_section = {
                    'title': title,
                    'level': level,
                    'content': [line]
                }
            else:
                current_section['content'].append(line)
        
        # Add last section
        if current_section['content']:
            sections.append(current_section)
        
        # Chunk each section
        chunk_index = 0
        for section in sections:
            section_text = '\n'.join(section['content'])
            
            # Restore code blocks
            for i, code_block in enumerate(code_blocks):
                section_text = section_text.replace(f"__CODE_BLOCK_{i}__", code_block)
            
            section_metadata = metadata.copy() if metadata else {}
            section_metadata['section_title'] = section['title']
            
            # Use semantic chunker for section content
            semantic_chunker = SemanticChunker(
                self.chunk_size, self.chunk_overlap, self.min_chunk_size
            )
            section_chunks = semantic_chunker.chunk(section_text, section_metadata)
            
            for chunk_text, chunk_meta in section_chunks:
                chunk_meta.chunk_index = chunk_index
                chunks.append((chunk_text, chunk_meta))
                chunk_index += 1
        
        return chunks


class CodeChunker(ChunkingStrategy):
    """Specialized chunker for code files"""
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk code by functions and classes"""
        chunks = []
        language = metadata.get('language', 'python') if metadata else 'python'
        
        if language == 'python':
            return self._chunk_python(text, metadata)
        else:
            # Fallback to line-based chunking
            return self._chunk_by_lines(text, metadata)
    
    def _chunk_python(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, ChunkMetadata]]:
        """Chunk Python code by functions and classes"""
        chunks = []
        
        # Patterns for Python structures
        class_pattern = r'^class\s+\w+.*?:(?:\n(?:\s{4,}.*|\s*\n))*'
        function_pattern = r'^def\s+\w+.*?:(?:\n(?:\s{4,}.*|\s*\n))*'
        
        # Find all classes and functions
        structures = []
        
        for match in re.finditer(class_pattern, text, re.MULTILINE):
            structures.append({
                'type': 'class',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0)
            })
        
        for match in re.finditer(function_pattern, text, re.MULTILINE):
            structures.append({
                'type': 'function',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0)
            })
        
        # Sort by start position
        structures.sort(key=lambda x: x['start'])
        
        # Create chunks
        chunk_index = 0
        last_end = 0
        
        # Add any imports or top-level code before first structure
        if structures and structures[0]['start'] > 0:
            header_text = text[:structures[0]['start']].strip()
            if header_text:
                chunks.append(self._create_code_chunk(
                    header_text, chunk_index, 0, 'header', metadata
                ))
                chunk_index += 1
        
        # Add structures as chunks
        for structure in structures:
            # Check if structure is too large
            if self.count_tokens(structure['text']) > self.chunk_size:
                # Split large structure
                lines = structure['text'].split('\n')
                current_chunk_lines = []
                current_tokens = 0
                
                for line in lines:
                    line_tokens = self.count_tokens(line + '\n')
                    if current_tokens + line_tokens > self.chunk_size and current_chunk_lines:
                        chunk_text = '\n'.join(current_chunk_lines)
                        chunks.append(self._create_code_chunk(
                            chunk_text, chunk_index, structure['start'], 
                            structure['type'], metadata
                        ))
                        chunk_index += 1
                        current_chunk_lines = [line]
                        current_tokens = line_tokens
                    else:
                        current_chunk_lines.append(line)
                        current_tokens += line_tokens
                
                if current_chunk_lines:
                    chunk_text = '\n'.join(current_chunk_lines)
                    chunks.append(self._create_code_chunk(
                        chunk_text, chunk_index, structure['start'], 
                        structure['type'], metadata
                    ))
                    chunk_index += 1
            else:
                chunks.append(self._create_code_chunk(
                    structure['text'], chunk_index, structure['start'], 
                    structure['type'], metadata
                ))
                chunk_index += 1
            
            last_end = structure['end']
        
        # Add any remaining code
        if last_end < len(text):
            remaining_text = text[last_end:].strip()
            if remaining_text:
                chunks.append(self._create_code_chunk(
                    remaining_text, chunk_index, last_end, 'footer', metadata
                ))
        
        return chunks
    
    def _chunk_by_lines(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, ChunkMetadata]]:
        """Fallback line-based chunking for code"""
        chunks = []
        lines = text.split('\n')
        
        current_chunk_lines = []
        current_tokens = 0
        chunk_index = 0
        current_start = 0
        
        for line in lines:
            line_tokens = self.count_tokens(line + '\n')
            
            if current_tokens + line_tokens > self.chunk_size and current_chunk_lines:
                chunk_text = '\n'.join(current_chunk_lines)
                chunks.append(self._create_code_chunk(
                    chunk_text, chunk_index, current_start, 'code', metadata
                ))
                chunk_index += 1
                current_start += len(chunk_text) + 1
                current_chunk_lines = [line]
                current_tokens = line_tokens
            else:
                current_chunk_lines.append(line)
                current_tokens += line_tokens
        
        if current_chunk_lines:
            chunk_text = '\n'.join(current_chunk_lines)
            chunks.append(self._create_code_chunk(
                chunk_text, chunk_index, current_start, 'code', metadata
            ))
        
        return chunks
    
    def _create_code_chunk(self, text: str, index: int, start: int, 
                          code_type: str, metadata: Dict) -> Tuple[str, ChunkMetadata]:
        """Create code chunk with metadata"""
        import uuid
        
        chunk_metadata = ChunkMetadata(
            chunk_id=str(uuid.uuid4()),
            chunk_index=index,
            start_char=start,
            end_char=start + len(text),
            word_count=len(text.split()),
            token_count=self.count_tokens(text),
            has_code=True,
            language=metadata.get('language', 'unknown') if metadata else 'unknown',
            section_title=f"{code_type}_{index}",
            page_number=metadata.get('page_number') if metadata else None
        )
        
        return text, chunk_metadata


def get_chunker(content_type: str = 'text', **kwargs) -> ChunkingStrategy:
    """Factory function to get appropriate chunker"""
    chunkers = {
        'text': SemanticChunker,
        'markdown': MarkdownChunker,
        'code': CodeChunker,
        'sentence': SentenceChunker
    }
    
    chunker_class = chunkers.get(content_type, SemanticChunker)
    return chunker_class(**kwargs)