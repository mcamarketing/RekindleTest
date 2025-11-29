"""
Data Pipeline Module

Handles data ingestion, processing, RAG (Retrieval-Augmented Generation),
vector embeddings, and data freshness management for the Rekindle Brain.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .config import BrainConfig

logger = logging.getLogger(__name__)

class DataPipeline:
    """Manages data ingestion, processing, and RAG for the Rekindle Brain"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.vector_db = None
        self.data_freshness: Dict[str, datetime] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        self.max_history_size = 10000

    async def initialize(self):
        """Initialize data pipeline components"""
        logger.info("Initializing DataPipeline")

        # Initialize vector database
        await self._initialize_vector_db()

        # Load existing data if available
        await self._load_existing_data()

        logger.info("DataPipeline initialized")

    async def _initialize_vector_db(self):
        """Initialize vector database for RAG"""
        db_config = self.config.data_config["vector_db"]

        if db_config["type"] == "weaviate":
            await self._initialize_weaviate(db_config)
        elif db_config["type"] == "qdrant":
            await self._initialize_qdrant(db_config)
        else:
            logger.warning(f"Unsupported vector DB type: {db_config['type']}, using mock")
            self.vector_db = MockVectorDB()

    async def _initialize_weaviate(self, config: Dict[str, Any]):
        """Initialize Weaviate vector database"""
        try:
            import weaviate
            from weaviate.embedded import EmbeddedOptions

            # In production, this would connect to a Weaviate instance
            # For now, use embedded version
            client = weaviate.Client(
                embedded_options=EmbeddedOptions()
            )

            # Create schema if it doesn't exist
            collection_name = config["collection_name"]
            if not client.schema.exists(collection_name):
                schema = {
                    "class": collection_name,
                    "properties": [
                        {"name": "content", "dataType": ["text"]},
                        {"name": "metadata", "dataType": ["object"]},
                        {"name": "source", "dataType": ["string"]},
                        {"name": "timestamp", "dataType": ["date"]},
                        {"name": "embedding", "dataType": ["number[]"]}
                    ],
                    "vectorizer": "none"  # We'll provide our own embeddings
                }
                client.schema.create_class(schema)

            self.vector_db = WeaviateVectorDB(client, collection_name)
            logger.info("Weaviate vector database initialized")

        except ImportError:
            logger.warning("Weaviate not installed, using mock vector DB")
            self.vector_db = MockVectorDB()

    async def _initialize_qdrant(self, config: Dict[str, Any]):
        """Initialize Qdrant vector database"""
        try:
            from qdrant_client import QdrantClient

            # In production, this would connect to Qdrant instance
            client = QdrantClient(":memory:")  # In-memory for development

            collection_name = config["collection_name"]
            vector_size = config["vector_size"]

            # Create collection if it doesn't exist
            if not client.collection_exists(collection_name):
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config={"size": vector_size, "distance": config["distance_metric"]}
                )

            self.vector_db = QdrantVectorDB(client, collection_name)
            logger.info("Qdrant vector database initialized")

        except ImportError:
            logger.warning("Qdrant not installed, using mock vector DB")
            self.vector_db = MockVectorDB()

    async def _load_existing_data(self):
        """Load existing data from storage"""
        # This would load cached embeddings, interaction history, etc.
        logger.info("Loading existing data (placeholder)")

    async def retrieve_context(self, query: str, task_type: str = "general",
                             filters: Optional[Dict[str, Any]] = None,
                             limit: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context from RAG system

        Args:
            query: Search query
            task_type: Type of task for context filtering
            filters: Additional filters for search
            limit: Maximum number of results

        Returns:
            Retrieved documents with relevance scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)

            # Search vector database
            search_filters = self._build_search_filters(task_type, filters)
            results = await self.vector_db.search(
                query_embedding=query_embedding,
                filters=search_filters,
                limit=limit
            )

            # Format results
            documents = []
            for result in results:
                doc = {
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.0),
                    "source": result.get("source", "unknown")
                }
                documents.append(doc)

            logger.info(f"Retrieved {len(documents)} context documents for query")

            return {
                "query": query,
                "documents": documents,
                "total_found": len(documents),
                "search_filters": search_filters
            }

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return {
                "query": query,
                "documents": [],
                "total_found": 0,
                "error": str(e)
            }

    async def process_social_data(self, social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process social media data for RAG ingestion

        Args:
            social_data: Raw social media posts/comments

        Returns:
            Processed data ready for embedding
        """
        logger.info(f"Processing {len(social_data)} social data items")

        processed_data = []

        for item in social_data:
            try:
                # Extract and clean content
                content = self._extract_social_content(item)
                if not content or len(content) < 20:  # Skip too short content
                    continue

                # Apply privacy filters
                filtered_content = self._apply_privacy_filters(content)
                if not filtered_content:
                    continue

                # Extract metadata
                metadata = self._extract_social_metadata(item)

                # Create processed item
                processed_item = {
                    "content": filtered_content,
                    "metadata": metadata,
                    "source": item.get("platform", "unknown"),
                    "timestamp": item.get("timestamp", datetime.now().isoformat()),
                    "processed_at": datetime.now().isoformat()
                }

                processed_data.append(processed_item)

            except Exception as e:
                logger.warning(f"Failed to process social item: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_data)} social data items")

        return processed_data

    async def update_embeddings(self, processed_data: List[Dict[str, Any]]):
        """Update vector database with new embeddings"""
        logger.info(f"Updating embeddings for {len(processed_data)} items")

        for item in processed_data:
            try:
                # Generate embedding
                embedding = await self._generate_embedding(item["content"])

                # Add to vector database
                await self.vector_db.add(
                    content=item["content"],
                    embedding=embedding,
                    metadata=item["metadata"],
                    source=item["source"],
                    timestamp=item["timestamp"]
                )

            except Exception as e:
                logger.error(f"Failed to update embedding: {e}")
                continue

        # Update freshness timestamp
        self.data_freshness["social_embeddings"] = datetime.now()

        logger.info("Embeddings updated successfully")

    async def store_interaction(self, interaction: Dict[str, Any]):
        """Store user interaction for learning"""
        # Add timestamp
        interaction["stored_at"] = datetime.now().isoformat()

        # Add to history
        self.interaction_history.append(interaction)

        # Maintain max history size
        if len(self.interaction_history) > self.max_history_size:
            self.interaction_history = self.interaction_history[-self.max_history_size:]

        # Could also store in vector DB for future retrieval
        logger.debug("Interaction stored for learning")

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using configured model"""
        # In production, this would use OpenAI Ada, local model, or other embedding service
        # For now, return mock embeddings

        import hashlib
        import math

        # Simple deterministic mock embedding based on text hash
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)

        # Generate pseudo-random but deterministic vector
        embedding_size = self.config.data_config["embedding_model"]["dimensions"]
        embedding = []

        for i in range(embedding_size):
            # Use hash to generate consistent "random" values
            value = math.sin(hash_int + i) * 0.5  # Scale to reasonable range
            embedding.append(value)

        # Normalize to unit vector (approximate)
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]

        return embedding

    def _build_search_filters(self, task_type: str, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build search filters for vector database"""
        search_filters = {
            "task_type": task_type
        }

        if filters:
            search_filters.update(filters)

        # Add time-based filters for freshness
        if "max_age_days" not in search_filters:
            search_filters["max_age_days"] = 90  # Default 90 days

        return search_filters

    def _extract_social_content(self, item: Dict[str, Any]) -> str:
        """Extract main content from social media item"""
        # Try different content fields
        content_fields = ["text", "content", "body", "message", "post"]

        for field in content_fields:
            if field in item and item[field]:
                return str(item[field])

        return ""

    def _apply_privacy_filters(self, content: str) -> str:
        """Apply privacy filters to content"""
        filtered_content = content

        for pattern in self.config.security_config["privacy_filters"]:
            import re
            filtered_content = re.sub(pattern, "[REDACTED]", filtered_content, flags=re.IGNORECASE)

        return filtered_content

    def _extract_social_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from social media item"""
        metadata = {
            "platform": item.get("platform", "unknown"),
            "author": item.get("author", "anonymous"),
            "engagement": {
                "likes": item.get("likes", 0),
                "shares": item.get("shares", 0),
                "comments": item.get("comments", 0)
            },
            "topics": item.get("topics", []),
            "sentiment": item.get("sentiment", "neutral")
        }

        return metadata

    async def get_data_freshness(self) -> Dict[str, Any]:
        """Get data freshness information"""
        now = datetime.now()

        freshness_info = {}
        for data_type, last_update in self.data_freshness.items():
            age_hours = (now - last_update).total_seconds() / 3600
            freshness_info[data_type] = {
                "last_update": last_update.isoformat(),
                "age_hours": age_hours,
                "is_fresh": age_hours < 24  # Consider fresh if < 24 hours
            }

        return freshness_info

    async def cleanup_old_data(self, max_age_days: int = 90):
        """Clean up old data from vector database"""
        logger.info(f"Cleaning up data older than {max_age_days} days")

        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        try:
            deleted_count = await self.vector_db.delete_older_than(cutoff_date)
            logger.info(f"Cleaned up {deleted_count} old data items")

        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get data pipeline statistics"""
        return {
            "vector_db_stats": await self.vector_db.get_stats() if self.vector_db else {},
            "interaction_history_size": len(self.interaction_history),
            "data_freshness": await self.get_data_freshness(),
            "total_processed_items": sum(len(h.get("documents", [])) for h in self.interaction_history)
        }

    async def shutdown(self):
        """Shutdown data pipeline"""
        logger.info("Shutting down DataPipeline")

        if self.vector_db:
            await self.vector_db.close()

        # Clear caches
        self.interaction_history.clear()
        self.data_freshness.clear()

        logger.info("DataPipeline shutdown complete")


# Vector Database Adapters

class MockVectorDB:
    """Mock vector database for development"""

    def __init__(self):
        self.data = []

    async def search(self, query_embedding, filters=None, limit=5):
        # Return mock results
        return [
            {
                "content": "Mock business strategy content",
                "metadata": {"source": "mock", "relevance": 0.8},
                "score": 0.8
            }
        ] * min(limit, 3)

    async def add(self, content, embedding, metadata, source, timestamp):
        self.data.append({
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
            "source": source,
            "timestamp": timestamp
        })

    async def delete_older_than(self, cutoff_date):
        return 0

    async def get_stats(self):
        return {"total_items": len(self.data), "type": "mock"}

    async def close(self):
        pass


class WeaviateVectorDB:
    """Weaviate vector database adapter"""

    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name

    async def search(self, query_embedding, filters=None, limit=5):
        # Implement Weaviate search
        pass

    async def add(self, content, embedding, metadata, source, timestamp):
        # Implement Weaviate add
        pass

    async def delete_older_than(self, cutoff_date):
        # Implement Weaviate delete
        pass

    async def get_stats(self):
        return {"type": "weaviate", "collection": self.collection_name}

    async def close(self):
        if self.client:
            self.client.close()


class QdrantVectorDB:
    """Qdrant vector database adapter"""

    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name

    async def search(self, query_embedding, filters=None, limit=5):
        # Implement Qdrant search
        pass

    async def add(self, content, embedding, metadata, source, timestamp):
        # Implement Qdrant add
        pass

    async def delete_older_than(self, cutoff_date):
        # Implement Qdrant delete
        pass

    async def get_stats(self):
        return {"type": "qdrant", "collection": self.collection_name}

    async def close(self):
        pass