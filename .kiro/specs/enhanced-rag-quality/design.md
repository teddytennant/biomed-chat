# Design Document: Enhanced RAG Quality

## Overview

This design enhances the existing FlexibleRAGPipeline with three key components: query optimization, hybrid search, and cross-encoder reranking. The architecture maintains backward compatibility while providing significant improvements in retrieval quality through a modular, composable design.

The enhancement follows a pipeline pattern where each component can be independently enabled or disabled:
1. Query Optimizer transforms user queries into optimized search queries
2. Hybrid Search combines semantic and keyword-based retrieval
3. Reranker scores and reorders results using a cross-encoder model

## Architecture

### High-Level Flow

```
User Query
    ↓
Query Optimizer (optional)
    ↓
Hybrid Search Engine
    ├─→ Semantic Search (FAISS)
    └─→ Keyword Search (BM25)
    ↓
Result Fusion (Reciprocal Rank Fusion)
    ↓
Reranker (optional)
    ↓
Top-K Results → LLM Context
```

### Component Interaction

The enhanced RAG system extends FlexibleRAGPipeline through composition rather than inheritance:

- **EnhancedRAGPipeline**: Orchestrates the enhanced retrieval flow
- **QueryOptimizer**: Preprocesses queries before retrieval
- **BM25Index**: Provides keyword-based search capabilities
- **CrossEncoderReranker**: Reorders results by relevance

All components are optional and fail gracefully to maintain system reliability.

## Components and Interfaces

### 1. QueryOptimizer

**Purpose**: Transform user queries to improve retrieval through expansion and reformulation.

**Interface**:
```python
class QueryOptimizer:
    def __init__(
        self,
        *,
        expansion_terms: Dict[str, List[str]] = None,
        acronym_map: Dict[str, List[str]] = None,
        max_expansions: int = 3,
    ):
        """Initialize query optimizer with domain knowledge."""
        
    def optimize(self, query: str) -> str:
        """
        Expand and optimize a query.
        
        Returns the optimized query string with expanded terms.
        Falls back to original query on any error.
        """
```

**Implementation Strategy**:
- Rule-based expansion using biomedical terminology dictionaries
- Acronym expansion (e.g., "ECG" → "ECG electrocardiogram")
- Synonym injection (e.g., "heart attack" → "heart attack myocardial infarction")
- Preserves original query terms to maintain intent

### 2. BM25Index

**Purpose**: Provide keyword-based search to complement semantic search.

**Interface**:
```python
class BM25Index:
    def __init__(
        self,
        *,
        k1: float = 1.5,
        b: float = 0.75,
        tokenizer: Callable[[str], List[str]] = None,
    ):
        """Initialize BM25 index with tuning parameters."""
        
    def add_documents(self, documents: List[DocumentChunk]) -> None:
        """Index documents for keyword search."""
        
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for documents matching query keywords.
        
        Returns list of (document_index, bm25_score) tuples.
        """
        
    def save(self, path: str) -> None:
        """Persist BM25 index to disk."""
        
    def load(self, path: str) -> None:
        """Load BM25 index from disk."""
```

**Implementation Strategy**:
- Use rank-bm25 library for efficient BM25 implementation
- Tokenize using biomedical-aware tokenizer (preserve hyphens, numbers)
- Store document IDs to map back to DocumentChunk objects
- Persist alongside FAISS index for consistency

### 3. CrossEncoderReranker

**Purpose**: Score query-document pairs to reorder results by true relevance.

**Interface**:
```python
class CrossEncoderReranker:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        *,
        batch_size: int = 32,
        timeout_seconds: float = 2.0,
    ):
        """Initialize cross-encoder reranker."""
        
    def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int = 3,
    ) -> List[SearchResult]:
        """
        Rerank search results by cross-encoder scores.
        
        Returns reordered results with updated scores.
        Falls back to original ordering on timeout or error.
        """
```

**Implementation Strategy**:
- Use sentence-transformers cross-encoder models
- Batch scoring for efficiency
- Timeout protection to prevent slow queries
- Update SearchResult.score with cross-encoder score

### 4. EnhancedRAGPipeline

**Purpose**: Orchestrate enhanced retrieval with all components.

**Interface**:
```python
class EnhancedRAGPipeline(FlexibleRAGPipeline):
    def __init__(
        self,
        embedding_model: str,
        *,
        enable_query_optimization: bool = True,
        enable_hybrid_search: bool = True,
        enable_reranking: bool = True,
        query_optimizer: QueryOptimizer = None,
        reranker: CrossEncoderReranker = None,
        bm25_index_path: str = None,
        **kwargs,
    ):
        """Initialize enhanced RAG pipeline."""
        
    def query(
        self,
        query_text: str,
        *,
        top_k: int = None,
        metadata_filters: Dict[str, Any] = None,
        candidate_multiplier: int = 3,
    ) -> List[SearchResult]:
        """
        Enhanced query with optimization, hybrid search, and reranking.
        
        Overrides parent query() method to add enhancements.
        """
```

**Implementation Strategy**:
- Extend FlexibleRAGPipeline to maintain compatibility
- Override query() method to inject enhancements
- Each enhancement is optional via configuration flags
- Graceful degradation on component failures

## Data Models

### SearchResult (Extended)

```python
@dataclass
class SearchResult:
    text: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str
    retrieval_method: str = "semantic"  # NEW: "semantic", "bm25", "hybrid"
    reranked: bool = False  # NEW: indicates if reranking was applied
```

### Configuration

```python
@dataclass
class EnhancedRAGConfig:
    # Query optimization
    enable_query_optimization: bool = True
    expansion_terms_path: Optional[str] = None
    acronym_map_path: Optional[str] = None
    
    # Hybrid search
    enable_hybrid_search: bool = True
    bm25_weight: float = 0.5
    semantic_weight: float = 0.5
    bm25_index_path: Optional[str] = None
    
    # Reranking
    enable_reranking: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_timeout: float = 2.0
    reranker_batch_size: int = 32
    
    # Retrieval parameters
    candidate_multiplier: int = 3  # Retrieve 3x candidates before reranking
```

## Corre
ctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Query expansion preserves original terms

*For any* user query, after query expansion, the expanded query string SHALL contain all non-stopword terms from the original query.
**Validates: Requirements 1.3**

### Property 2: Acronym expansion includes full forms

*For any* query containing a known acronym from the acronym map, the expanded query SHALL contain the full form of that acronym.
**Validates: Requirements 1.2**

### Property 3: Query optimization graceful fallback

*For any* query where optimization raises an exception, the system SHALL return the original unmodified query without propagating the error.
**Validates: Requirements 1.5**

### Property 4: Hybrid search invokes both methods

*For any* query when hybrid search is enabled, both semantic search and BM25 search SHALL be invoked and return results.
**Validates: Requirements 2.1**

### Property 5: Merged results contain no duplicates

*For any* hybrid search result set, no two results SHALL have the same chunk_id.
**Validates: Requirements 2.3**

### Property 6: Reciprocal rank fusion formula correctness

*For any* two ranked lists being merged, the reciprocal rank fusion score for each document SHALL equal the sum of 1/(rank + k) across all lists where the document appears, with k=60.
**Validates: Requirements 2.2**

### Property 7: BM25 fallback on unavailability

*For any* query when the BM25 index is None or uninitialized, hybrid search SHALL return only semantic search results without error.
**Validates: Requirements 2.5**

### Property 8: Reranked results are sorted descending

*For any* list of search results after reranking, the results SHALL be ordered by descending score (result[i].score >= result[i+1].score for all valid i).
**Validates: Requirements 3.2**

### Property 9: Top-k limiting after reranking

*For any* reranking operation with top_k parameter, the returned results SHALL have length equal to min(top_k, len(candidates)).
**Validates: Requirements 3.3**

### Property 10: Reranker timeout fallback

*For any* reranking operation that exceeds the timeout threshold, the system SHALL return the original candidate ordering without reranked scores.
**Validates: Requirements 3.5**

### Property 11: Reranker failure fallback

*For any* reranking operation where the cross-encoder model fails to load or score, the system SHALL return the original candidates with their original scores.
**Validates: Requirements 3.4**

### Property 12: Configuration flags control feature activation

*For any* EnhancedRAGPipeline instance, setting enable_query_optimization=False SHALL result in queries being passed directly to retrieval without expansion.
**Validates: Requirements 4.2**

### Property 13: Backward compatibility with parent interface

*For any* method defined in FlexibleRAGPipeline, the EnhancedRAGPipeline SHALL provide the same method with compatible signature and behavior.
**Validates: Requirements 4.1**

### Property 14: Component failures log and continue

*For any* enhancement component (query optimizer, BM25, reranker) that raises an exception, the system SHALL log the error and continue execution with the degraded functionality.
**Validates: Requirements 4.5**

## Error Handling

### Query Optimizer Errors
- **Expansion failure**: Return original query, log warning
- **Invalid acronym map**: Skip acronym expansion, continue with synonym expansion
- **Empty query**: Return empty string without expansion

### BM25 Index Errors
- **Index not initialized**: Fall back to semantic-only search
- **Tokenization failure**: Skip BM25 search, use semantic results only
- **Index corruption**: Log error, rebuild index on next add_documents call

### Reranker Errors
- **Model load failure**: Disable reranking, use original scores
- **Timeout exceeded**: Return original ordering, log timeout
- **Scoring exception**: Skip failed documents, rerank remaining
- **Empty candidate list**: Return empty list without error

### General Error Handling Principles
1. Never fail the entire query due to enhancement failures
2. Always log errors with sufficient context for debugging
3. Degrade gracefully to baseline RAG functionality
4. Provide clear error messages in logs
5. Track degradation events for monitoring

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

- **Query Optimizer**: Test known acronyms, empty queries, special characters
- **BM25 Index**: Test tokenization, document addition, persistence
- **Reranker**: Test score computation, timeout behavior, batch processing
- **Hybrid Search**: Test result merging, deduplication, weighting

### Property-Based Testing

Property-based tests will verify universal properties across diverse inputs using the Hypothesis library:

- **Property 1-14**: Each correctness property will have a dedicated property-based test
- **Test configuration**: Minimum 100 iterations per property test
- **Generators**: Custom generators for queries, documents, and search results
- **Shrinking**: Hypothesis will automatically find minimal failing examples

Each property-based test will be tagged with:
```python
# Feature: enhanced-rag-quality, Property X: [property description]
```

### Integration Testing

Integration tests will verify end-to-end behavior:

- Full pipeline with all enhancements enabled
- Degradation scenarios (components disabled or failing)
- Performance benchmarks (latency, throughput)
- Retrieval quality metrics (precision@k, recall@k, MRR)

### Test Data

- **Biomedical corpus**: Sample documents from FDA guidelines, IEC standards, medical literature
- **Query set**: Representative biomedical engineering queries with known relevant documents
- **Acronym map**: Common biomedical acronyms (ECG, MRI, FDA, IEC, etc.)
- **Synonym dictionary**: Domain-specific terminology variations

## Performance Considerations

### Latency Budget

- Query optimization: < 50ms
- Semantic search: < 100ms (existing)
- BM25 search: < 50ms
- Result fusion: < 10ms
- Reranking: < 2000ms (with timeout)
- **Total target**: < 2.5s for enhanced query

### Memory Usage

- BM25 index: ~10-20% of document corpus size
- Cross-encoder model: ~100MB GPU memory or ~400MB CPU memory
- Query optimizer: ~1MB for dictionaries

### Optimization Strategies

1. **Lazy loading**: Load reranker model only when first needed
2. **Caching**: Cache expanded queries for repeated queries
3. **Batch processing**: Rerank in batches for efficiency
4. **Parallel search**: Run semantic and BM25 searches concurrently
5. **Early termination**: Stop reranking if timeout approaching

## Configuration

### Environment Variables

```bash
# Enable/disable enhancements
RAG_ENABLE_QUERY_OPTIMIZATION=true
RAG_ENABLE_HYBRID_SEARCH=true
RAG_ENABLE_RERANKING=true

# Model paths
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
RAG_BM25_INDEX_PATH=./data/bm25_index.pkl

# Tuning parameters
RAG_CANDIDATE_MULTIPLIER=3
RAG_RERANKER_TIMEOUT=2.0
RAG_BM25_WEIGHT=0.5
```

### Python Configuration

```python
from enhanced_rag import EnhancedRAGPipeline, EnhancedRAGConfig

config = EnhancedRAGConfig(
    enable_query_optimization=True,
    enable_hybrid_search=True,
    enable_reranking=True,
    reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    candidate_multiplier=3,
)

pipeline = EnhancedRAGPipeline(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    config=config,
)
```

## Migration Path

### Phase 1: Add Components (Backward Compatible)
1. Implement QueryOptimizer, BM25Index, CrossEncoderReranker as standalone classes
2. Add comprehensive tests for each component
3. No changes to existing FlexibleRAGPipeline

### Phase 2: Create EnhancedRAGPipeline
1. Extend FlexibleRAGPipeline with enhanced query() method
2. All enhancements disabled by default for safety
3. Existing code continues to work unchanged

### Phase 3: Gradual Rollout
1. Enable query optimization in production (low risk)
2. Monitor latency and error rates
3. Enable hybrid search after validation
4. Enable reranking last (highest latency impact)

### Phase 4: Optimization
1. Tune weights and parameters based on production metrics
2. Add caching and performance optimizations
3. Consider upgrading to larger reranker models if beneficial

## Dependencies

### New Python Packages

```
rank-bm25>=0.2.2  # BM25 implementation
hypothesis>=6.0.0  # Property-based testing
```

### Existing Packages (Already in requirements.txt)

```
sentence-transformers>=2.2.2  # For cross-encoder models
faiss-cpu>=1.7.4  # Existing vector search
numpy>=1.24.0  # Existing
```

## Monitoring and Observability

### Metrics to Track

- **Retrieval quality**: Precision@k, Recall@k, MRR
- **Latency**: P50, P95, P99 for each component
- **Degradation events**: Count of fallbacks per component
- **Cache hit rates**: For query expansion cache
- **Error rates**: Per component and overall

### Logging

```python
logger.info("Query optimization expanded query", extra={
    "original_query": original,
    "expanded_query": expanded,
    "expansion_count": len(new_terms),
})

logger.warning("Reranker timeout exceeded", extra={
    "query": query,
    "timeout_ms": timeout * 1000,
    "candidate_count": len(candidates),
})
```

## Future Enhancements

1. **Neural query expansion**: Use LLM to generate query variations
2. **Learned fusion**: Train model to weight semantic vs keyword results
3. **Contextual reranking**: Use conversation history in reranking
4. **Adaptive timeouts**: Adjust reranker timeout based on query complexity
5. **Multi-vector retrieval**: Use ColBERT-style late interaction models
