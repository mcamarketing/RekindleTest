"""
ARE RAG Service Agent

Provides retrieval-augmented generation and long-term memory support.
Retrieves relevant context for each task, stores outcomes and learning signals,
and makes them available to Planner, Executor, and Critic when needed.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class MemoryChunk:
    """A chunk of stored memory"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    importance_score: float = 0.5

@dataclass
class ContextQuery:
    """A query for context retrieval"""
    query: str
    task_type: str
    agent_context: Dict[str, Any]
    max_results: int = 5
    similarity_threshold: float = 0.7
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievedContext:
    """Retrieved context with relevance scores"""
    chunks: List[MemoryChunk]
    total_found: int
    query: str
    retrieval_time: float
    average_relevance: float

class RagServiceAgent:
    """ARE RAG Service - Context retrieval and memory management"""

    def __init__(self):
        self.memory_store: Dict[str, MemoryChunk] = {}
        self.embedding_cache: Dict[str, List[float]] = {}
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)

        # Memory categories
        self.categories = {
            "outcomes": [],      # Task execution results
            "learnings": [],     # Learning signals and improvements
            "patterns": [],      # Successful strategies and templates
            "constraints": [],   # Safety rules and limitations
            "context": [],       # General contextual information
            "social_intel": []   # Social listening intelligence
        }

        # Initialize with some default knowledge
        self._initialize_default_knowledge()

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main RAG service execution method"""
        request_type = input_data.get("request_type", "retrieve")

        if request_type == "retrieve":
            return await self._handle_retrieval(input_data, context)
        elif request_type == "store":
            return await self._handle_storage(input_data, context)
        elif request_type == "store_social":
            return await self._handle_social_storage(input_data, context)
        elif request_type == "retrieve_social":
            return await self._handle_social_retrieval(input_data, context)
        elif request_type == "update":
            return await self._handle_update(input_data, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    async def _handle_retrieval(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle context retrieval requests"""
        query_data = input_data.get("query", {})
        query = ContextQuery(**query_data)

        logger.info(f"Retrieving context for query: {query.query[:50]}...")

        # Perform retrieval
        retrieved = await self._retrieve_context(query)

        # Update access patterns
        for chunk in retrieved.chunks:
            self._update_access_pattern(chunk.id)

        return {
            "retrieved_context": {
                "chunks": [
                    {
                        "id": chunk.id,
                        "content": chunk.content,
                        "metadata": chunk.metadata,
                        "relevance_score": self._calculate_relevance_score(chunk, query),
                        "timestamp": chunk.timestamp.isoformat()
                    } for chunk in retrieved.chunks
                ],
                "total_found": retrieved.total_found,
                "query": retrieved.query,
                "retrieval_time": retrieved.retrieval_time,
                "average_relevance": retrieved.average_relevance
            },
            "enriched_query": query.__dict__
        }

    async def _handle_storage(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle memory storage requests"""
        content = input_data.get("content", "")
        metadata = input_data.get("metadata", {})
        category = input_data.get("category", "context")

        if not content:
            raise ValueError("Content is required for storage")

        # Create memory chunk
        chunk_id = self._generate_chunk_id(content, metadata)
        chunk = MemoryChunk(
            id=chunk_id,
            content=content,
            metadata=metadata,
            importance_score=self._calculate_importance(content, metadata, category)
        )

        # Generate embedding (simplified - would use actual embedding model)
        chunk.embedding = await self._generate_embedding(content)

        # Store chunk
        self.memory_store[chunk_id] = chunk
        self.categories[category].append(chunk_id)

        # Maintain memory limits
        await self._maintain_memory_limits(category)

        logger.info(f"Stored memory chunk {chunk_id} in category {category}")

        return {
            "stored_chunk": {
                "id": chunk_id,
                "category": category,
                "importance_score": chunk.importance_score,
                "stored_at": chunk.timestamp.isoformat()
            }
        }

    async def _handle_update(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle memory update requests"""
        chunk_id = input_data.get("chunk_id")
        updates = input_data.get("updates", {})

        if not chunk_id or chunk_id not in self.memory_store:
            raise ValueError(f"Chunk {chunk_id} not found")

        chunk = self.memory_store[chunk_id]

        # Update chunk
        for key, value in updates.items():
            if hasattr(chunk, key):
                setattr(chunk, key, value)

        chunk.last_accessed = datetime.now()

        logger.info(f"Updated memory chunk {chunk_id}")

        return {
            "updated_chunk": {
                "id": chunk_id,
                "updates_applied": list(updates.keys()),
                "updated_at": chunk.last_accessed.isoformat()
            }
        }

    async def _handle_social_storage(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle social intelligence storage"""
        insights = input_data.get("insights", [])
        source = input_data.get("source", "social_listening")

        if not insights:
            return {"status": "no_insights", "stored_count": 0}

        stored_count = 0
        duplicates_skipped = 0

        for insight in insights:
            # Check for duplicates
            if await self._is_duplicate_insight(insight):
                duplicates_skipped += 1
                continue

            # Create memory chunk from insight
            content = self._format_social_insight_content(insight)
            metadata = {
                "source": source,
                "insight_type": insight.get("type", "general"),
                "sentiment": insight.get("sentiment", "neutral"),
                "confidence_score": insight.get("confidence_score", 0),
                "pain_points": insight.get("pain_points", []),
                "desires": insight.get("desires", []),
                "topic": insight.get("topic", ""),
                "data_freshness": datetime.now().isoformat(),
                "is_social_intel": True
            }

            # Store the insight
            storage_result = await self._handle_storage({
                "content": content,
                "metadata": metadata,
                "category": "social_intel"
            }, context)

            stored_count += 1

        logger.info(f"Stored {stored_count} social insights, skipped {duplicates_skipped} duplicates")

        return {
            "status": "stored",
            "stored_count": stored_count,
            "duplicates_skipped": duplicates_skipped,
            "total_insights": len(insights)
        }

    async def _handle_social_retrieval(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle social intelligence retrieval"""
        query = input_data.get("query", "")
        topics = input_data.get("topics", [])
        sentiment_filter = input_data.get("sentiment_filter")
        max_results = input_data.get("max_results", 10)

        # Create specialized query for social intel
        social_query = ContextQuery(
            query=query,
            task_type="social_intelligence",
            agent_context={"requires_social_context": True},
            max_results=max_results,
            filters={
                "is_social_intel": True,
                "topics": topics,
                "sentiment": sentiment_filter
            }
        )

        # Retrieve from social_intel category specifically
        retrieved = await self._retrieve_social_context(social_query)

        return {
            "retrieved_insights": [
                {
                    "id": chunk.id,
                    "content": chunk.content,
                    "sentiment": chunk.metadata.get("sentiment"),
                    "topic": chunk.metadata.get("topic"),
                    "confidence_score": chunk.metadata.get("confidence_score"),
                    "pain_points": chunk.metadata.get("pain_points", []),
                    "desires": chunk.metadata.get("desires", []),
                    "source": chunk.metadata.get("source"),
                    "relevance_score": self._calculate_relevance_score(chunk, social_query),
                    "timestamp": chunk.timestamp.isoformat()
                }
                for chunk in retrieved.chunks
            ],
            "total_found": retrieved.total_found,
            "query": retrieved.query,
            "retrieval_time": retrieved.retrieval_time
        }

    async def _retrieve_social_context(self, query: ContextQuery) -> RetrievedContext:
        """Retrieve social intelligence context"""
        start_time = datetime.now()

        # Focus on social_intel category
        candidates = []
        for chunk_id in self.categories["social_intel"]:
            chunk = self.memory_store.get(chunk_id)
            if chunk:
                candidates.append(chunk)

        # Apply filters
        if query.filters:
            filtered_candidates = []
            for chunk in candidates:
                if self._matches_social_filters(chunk, query.filters):
                    filtered_candidates.append(chunk)
            candidates = filtered_candidates

        # Rank by relevance
        ranked_chunks = await self._rank_chunks_by_relevance(candidates, query)

        # Filter by threshold and limit
        filtered_chunks = [
            chunk for chunk, score in ranked_chunks
            if score >= query.similarity_threshold
        ][:query.max_results]

        retrieval_time = (datetime.now() - start_time).total_seconds()
        avg_relevance = sum(self._calculate_relevance_score(chunk, query) for chunk in filtered_chunks) / len(filtered_chunks) if filtered_chunks else 0

        return RetrievedContext(
            chunks=filtered_chunks,
            total_found=len(candidates),
            query=query.query,
            retrieval_time=retrieval_time,
            average_relevance=avg_relevance
        )

    def _matches_social_filters(self, chunk: MemoryChunk, filters: Dict[str, Any]) -> bool:
        """Check if social chunk matches filters"""
        # Check topics filter
        if "topics" in filters and filters["topics"]:
            chunk_topic = chunk.metadata.get("topic", "").lower()
            filter_topics = [t.lower() for t in filters["topics"]]
            if not any(topic in chunk_topic for topic in filter_topics):
                return False

        # Check sentiment filter
        if "sentiment" in filters and filters["sentiment"]:
            chunk_sentiment = chunk.metadata.get("sentiment", "")
            if chunk_sentiment != filters["sentiment"]:
                return False

        return True

    async def _is_duplicate_insight(self, insight: Dict[str, Any]) -> bool:
        """Check if insight is a duplicate"""
        insight_content = self._format_social_insight_content(insight)

        # Simple duplicate check - in production, use more sophisticated methods
        for chunk in self.memory_store.values():
            if chunk.metadata.get("is_social_intel"):
                # Check content similarity
                similarity = self._calculate_content_similarity(chunk.content, insight_content)
                if similarity > 0.9:  # Very high similarity = duplicate
                    return True

        return False

    def _format_social_insight_content(self, insight: Dict[str, Any]) -> str:
        """Format social insight into storable content"""
        content_parts = []

        if insight.get("topic"):
            content_parts.append(f"Topic: {insight['topic']}")

        if insight.get("anonymized_content"):
            content_parts.append(f"Content: {insight['anonymized_content']}")

        if insight.get("pain_points"):
            content_parts.append(f"Pain Points: {', '.join(insight['pain_points'])}")

        if insight.get("desires"):
            content_parts.append(f"Desires: {', '.join(insight['desires'])}")

        if insight.get("objections"):
            content_parts.append(f"Objections: {', '.join(insight['objections'])}")

        return " | ".join(content_parts)

    async def _retrieve_context(self, query: ContextQuery) -> RetrievedContext:
        """Retrieve relevant context for a query"""
        start_time = datetime.now()

        # Find candidate chunks
        candidates = await self._find_candidate_chunks(query)

        # Rank by relevance
        ranked_chunks = await self._rank_chunks_by_relevance(candidates, query)

        # Filter by threshold and limit
        filtered_chunks = [
            chunk for chunk, score in ranked_chunks
            if score >= query.similarity_threshold
        ][:query.max_results]

        retrieval_time = (datetime.now() - start_time).total_seconds()
        avg_relevance = sum(self._calculate_relevance_score(chunk, query) for chunk in filtered_chunks) / len(filtered_chunks) if filtered_chunks else 0

        return RetrievedContext(
            chunks=filtered_chunks,
            total_found=len(candidates),
            query=query.query,
            retrieval_time=retrieval_time,
            average_relevance=avg_relevance
        )

    async def _find_candidate_chunks(self, query: ContextQuery) -> List[MemoryChunk]:
        """Find candidate memory chunks for a query"""
        candidates = []

        # Search by category relevance
        relevant_categories = self._get_relevant_categories(query.task_type)

        for category in relevant_categories:
            for chunk_id in self.categories[category]:
                chunk = self.memory_store.get(chunk_id)
                if chunk:
                    candidates.append(chunk)

        # Also search by metadata filters
        if query.filters:
            filtered_candidates = []
            for chunk in candidates:
                if self._matches_filters(chunk, query.filters):
                    filtered_candidates.append(chunk)
            candidates = filtered_candidates

        return candidates

    async def _rank_chunks_by_relevance(self, chunks: List[MemoryChunk], query: ContextQuery) -> List[Tuple[MemoryChunk, float]]:
        """Rank chunks by relevance to query"""
        ranked = []

        for chunk in chunks:
            relevance_score = self._calculate_relevance_score(chunk, query)
            ranked.append((chunk, relevance_score))

        # Sort by relevance score descending
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked

    def _calculate_relevance_score(self, chunk: MemoryChunk, query: ContextQuery) -> float:
        """Calculate relevance score between chunk and query"""
        score = 0.0

        # Content similarity (simplified - would use actual embedding similarity)
        content_similarity = self._calculate_content_similarity(chunk.content, query.query)
        score += content_similarity * 0.6

        # Metadata relevance
        metadata_relevance = self._calculate_metadata_relevance(chunk.metadata, query.agent_context)
        score += metadata_relevance * 0.2

        # Recency bonus
        recency_score = self._calculate_recency_score(chunk)
        score += recency_score * 0.1

        # Importance bonus
        score += chunk.importance_score * 0.1

        return min(score, 1.0)

    def _calculate_content_similarity(self, content: str, query: str) -> float:
        """Calculate content similarity (simplified)"""
        # Simple word overlap similarity
        content_words = set(content.lower().split())
        query_words = set(query.lower().split())

        if not content_words or not query_words:
            return 0.0

        intersection = content_words.intersection(query_words)
        union = content_words.union(query_words)

        return len(intersection) / len(union)

    def _calculate_metadata_relevance(self, metadata: Dict[str, Any], agent_context: Dict[str, Any]) -> float:
        """Calculate metadata relevance"""
        relevance = 0.0
        matches = 0

        # Check for matching agent types
        chunk_agent = metadata.get("agent_type")
        context_agent = agent_context.get("agent_type")
        if chunk_agent and context_agent and chunk_agent == context_agent:
            relevance += 0.3
            matches += 1

        # Check for matching task types
        chunk_task = metadata.get("task_type")
        context_task = agent_context.get("task_type")
        if chunk_task and context_task and chunk_task == context_task:
            relevance += 0.3
            matches += 1

        # Check for org/user context
        chunk_org = metadata.get("org_id")
        context_org = agent_context.get("org_id")
        if chunk_org and context_org and chunk_org == context_org:
            relevance += 0.2
            matches += 1

        return relevance if matches > 0 else 0.0

    def _calculate_recency_score(self, chunk: MemoryChunk) -> float:
        """Calculate recency score (newer = higher score)"""
        hours_old = (datetime.now() - chunk.timestamp).total_seconds() / 3600

        # Exponential decay: score = e^(-hours_old/24) for first 7 days, then flat
        if hours_old <= 168:  # 7 days
            import math
            return math.exp(-hours_old / 24)
        else:
            return 0.1  # Minimum recency score

    def _calculate_importance(self, content: str, metadata: Dict[str, Any], category: str) -> float:
        """Calculate importance score for a memory chunk"""
        importance = 0.5  # Base importance

        # Category-based importance
        category_weights = {
            "learnings": 0.9,       # Learning signals are very important
            "constraints": 0.8,     # Safety rules are critical
            "social_intel": 0.75,   # Social intelligence is highly valuable
            "outcomes": 0.7,        # Results are valuable
            "patterns": 0.6,        # Templates are useful
            "context": 0.4          # General context is least important
        }
        importance *= category_weights.get(category, 0.5)

        # Content length bonus (longer content often more valuable)
        content_length = len(content.split())
        if content_length > 100:
            importance *= 1.2
        elif content_length < 20:
            importance *= 0.8

        # Metadata indicators
        if metadata.get("is_successful"):
            importance *= 1.3
        if metadata.get("has_learning_signal"):
            importance *= 1.4
        if metadata.get("is_anomaly"):
            importance *= 1.2

        return min(importance, 1.0)

    async def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for content (simplified)"""
        # In a real implementation, this would call an embedding model
        # For now, create a simple hash-based pseudo-embedding
        content_hash = hashlib.md5(content.encode()).hexdigest()
        embedding = [int(content_hash[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]
        return embedding[:16]  # 16-dimensional embedding

    async def _maintain_memory_limits(self, category: str):
        """Maintain memory limits by removing least important chunks"""
        max_chunks_per_category = 1000

        if len(self.categories[category]) > max_chunks_per_category:
            # Sort chunks by importance and recency
            category_chunks = [
                self.memory_store[chunk_id] for chunk_id in self.categories[category]
                if chunk_id in self.memory_store
            ]

            category_chunks.sort(key=lambda c: (c.importance_score, c.timestamp), reverse=True)

            # Keep only the top chunks
            keep_chunks = category_chunks[:max_chunks_per_category]
            self.categories[category] = [chunk.id for chunk in keep_chunks]

            # Remove excess chunks from memory store
            excess_ids = [chunk.id for chunk in category_chunks[max_chunks_per_category:]]
            for chunk_id in excess_ids:
                if chunk_id in self.memory_store:
                    del self.memory_store[chunk_id]

            logger.info(f"Cleaned up {len(excess_ids)} chunks from category {category}")

    def _get_relevant_categories(self, task_type: str) -> List[str]:
        """Get relevant memory categories for a task type"""
        category_mapping = {
            "planning": ["learnings", "patterns", "context", "social_intel"],
            "execution": ["outcomes", "constraints", "patterns", "social_intel"],
            "evaluation": ["learnings", "outcomes", "constraints", "social_intel"],
            "content_generation": ["patterns", "learnings", "context", "social_intel"],
            "analysis": ["outcomes", "learnings", "context", "social_intel"],
            "optimization": ["learnings", "patterns", "outcomes", "social_intel"],
            "social_intelligence": ["social_intel", "learnings", "context"]
        }

        return category_mapping.get(task_type, ["context", "patterns"])

    def _matches_filters(self, chunk: MemoryChunk, filters: Dict[str, Any]) -> bool:
        """Check if chunk matches metadata filters"""
        for key, value in filters.items():
            chunk_value = chunk.metadata.get(key)
            if chunk_value != value:
                return False
        return True

    def _generate_chunk_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for memory chunk"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:8]
        timestamp = str(int(datetime.now().timestamp()))

        return f"chunk_{content_hash}_{metadata_hash}_{timestamp}"

    def _update_access_pattern(self, chunk_id: str):
        """Update access pattern for a chunk"""
        self.access_patterns[chunk_id].append(datetime.now())

        # Keep only last 100 accesses
        if len(self.access_patterns[chunk_id]) > 100:
            self.access_patterns[chunk_id] = self.access_patterns[chunk_id][-100:]

        # Update chunk metadata
        if chunk_id in self.memory_store:
            chunk = self.memory_store[chunk_id]
            chunk.access_count += 1
            chunk.last_accessed = datetime.now()

    def _initialize_default_knowledge(self):
        """Initialize with default knowledge chunks"""
        default_chunks = [
            {
                "content": "Successful revival campaigns typically include personalized value propositions and clear next steps.",
                "metadata": {"category": "pattern", "task_type": "revival", "confidence": 0.9},
                "category": "patterns"
            },
            {
                "content": "Content with high personalization scores (>0.8) achieve 2.3x higher reply rates.",
                "metadata": {"category": "learning", "task_type": "content_generation", "source": "outcome_analysis"},
                "category": "learnings"
            },
            {
                "content": "Never send more than 1000 emails per day per organization to avoid deliverability issues.",
                "metadata": {"category": "constraint", "type": "rate_limit", "severity": "high"},
                "category": "constraints"
            },
            {
                "content": "Brain agent performs best with specific, constrained prompts rather than open-ended requests.",
                "metadata": {"category": "pattern", "agent_type": "brain", "optimization_tip": True},
                "category": "patterns"
            }
        ]

        for chunk_data in default_chunks:
            content = chunk_data["content"]
            metadata = chunk_data["metadata"]
            category = chunk_data["category"]

            chunk_id = self._generate_chunk_id(content, metadata)
            chunk = MemoryChunk(
                id=chunk_id,
                content=content,
                metadata=metadata,
                importance_score=self._calculate_importance(content, metadata, category)
            )

            self.memory_store[chunk_id] = chunk
            self.categories[category].append(chunk_id)

        logger.info(f"Initialized {len(default_chunks)} default knowledge chunks")

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_chunks = len(self.memory_store)
        category_stats = {cat: len(chunks) for cat, chunks in self.categories.items()}

        # Calculate average importance and recency
        if total_chunks > 0:
            avg_importance = sum(chunk.importance_score for chunk in self.memory_store.values()) / total_chunks
            recent_chunks = sum(1 for chunk in self.memory_store.values()
                              if chunk.timestamp > datetime.now() - timedelta(hours=24))
        else:
            avg_importance = 0
            recent_chunks = 0

        return {
            "total_chunks": total_chunks,
            "category_breakdown": category_stats,
            "average_importance": avg_importance,
            "recent_chunks_24h": recent_chunks,
            "generated_at": datetime.now().isoformat()
        }

    async def cleanup_old_memories(self, days_old: int = 90):
        """Clean up old, low-importance memories"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0

        chunks_to_remove = []
        for chunk_id, chunk in self.memory_store.items():
            # Remove if old and low importance
            if chunk.timestamp < cutoff_date and chunk.importance_score < 0.3:
                chunks_to_remove.append(chunk_id)

        for chunk_id in chunks_to_remove:
            chunk = self.memory_store[chunk_id]
            # Remove from categories
            for category, chunk_ids in self.categories.items():
                if chunk_id in chunk_ids:
                    self.categories[category].remove(chunk_id)

            # Remove from memory store
            del self.memory_store[chunk_id]
            removed_count += 1

        logger.info(f"Cleaned up {removed_count} old memory chunks")
        return {"removed_chunks": removed_count}