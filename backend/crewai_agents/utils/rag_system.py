"""
RAG (Retrieval-Augmented Generation) System

Stores and retrieves best practices, successful patterns, and learnings
from all clients to continuously improve agent performance.

This is the "collective intelligence" that all agents learn from.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from ..tools.db_tools import SupabaseDB


@dataclass
class BestPractice:
    """A best practice or successful pattern."""
    id: Optional[str]
    category: str  # "email", "subject_line", "sequence", "timing", "channel", etc.
    content: str  # The actual content (email body, subject line, etc.)
    performance_metrics: Dict[str, float]  # {"open_rate": 0.67, "reply_rate": 0.23, "meeting_rate": 0.15}
    context: Dict[str, Any]  # Lead type, industry, ACV range, etc.
    success_score: float  # Calculated from metrics
    usage_count: int  # How many times this has been used
    success_count: int  # How many times it succeeded
    created_at: str
    updated_at: str
    tags: List[str]  # For easier retrieval


class RAGSystem:
    """
    RAG System for storing and retrieving best practices.
    
    This system:
    - Stores successful emails, subject lines, sequences
    - Tracks performance metrics
    - Retrieves similar successful patterns
    - Continuously learns from all clients
    """
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.table_name = "best_practices_rag"
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the best_practices_rag table exists."""
        # In production, this would be a migration
        # For now, we'll use Supabase table directly
        pass
    
    def store_best_practice(
        self,
        category: str,
        content: str,
        performance_metrics: Dict[str, float],
        context: Dict[str, Any],
        tags: List[str] = None
    ) -> str:
        """
        Store a best practice in the RAG system.
        
        Args:
            category: Type of practice (email, subject_line, sequence, etc.)
            content: The actual content
            performance_metrics: Performance data (open_rate, reply_rate, etc.)
            context: Context about when/where it worked
            tags: Optional tags for retrieval
        
        Returns:
            ID of stored practice
        """
        # Calculate success score
        success_score = self._calculate_success_score(performance_metrics)
        
        # Create best practice
        practice = BestPractice(
            id=None,
            category=category,
            content=content,
            performance_metrics=performance_metrics,
            context=context,
            success_score=success_score,
            usage_count=0,
            success_count=0,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            tags=tags or []
        )
        
        # Store in database
        result = self.db.supabase.table(self.table_name).insert({
            "category": practice.category,
            "content": practice.content,
            "performance_metrics": json.dumps(practice.performance_metrics),
            "context": json.dumps(practice.context),
            "success_score": practice.success_score,
            "usage_count": practice.usage_count,
            "success_count": practice.success_count,
            "tags": practice.tags,
            "created_at": practice.created_at,
            "updated_at": practice.updated_at
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        return None
    
    def retrieve_similar_practices(
        self,
        category: str,
        context: Dict[str, Any],
        limit: int = 5,
        min_success_score: float = 0.7
    ) -> List[BestPractice]:
        """
        Retrieve similar best practices based on category and context.
        
        Args:
            category: Type of practice to retrieve
            context: Context to match against (industry, ACV, etc.)
            limit: Maximum number of practices to return
            min_success_score: Minimum success score threshold
        
        Returns:
            List of best practices sorted by relevance
        """
        # Query database for similar practices
        query = self.db.supabase.table(self.table_name).select("*").eq(
            "category", category
        ).gte("success_score", min_success_score).order(
            "success_score", desc=True
        ).limit(limit)
        
        result = query.execute()
        
        practices = []
        for row in result.data or []:
            # Calculate relevance score based on context matching
            relevance = self._calculate_relevance(row.get("context", {}), context)
            
            practice = BestPractice(
                id=row["id"],
                category=row["category"],
                content=row["content"],
                performance_metrics=json.loads(row.get("performance_metrics", "{}")),
                context=json.loads(row.get("context", "{}")),
                success_score=row["success_score"],
                usage_count=row.get("usage_count", 0),
                success_count=row.get("success_count", 0),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                tags=row.get("tags", [])
            )
            
            # Add relevance score
            practice.relevance_score = relevance
            practices.append(practice)
        
        # Sort by relevance * success_score
        practices.sort(key=lambda p: p.relevance_score * p.success_score, reverse=True)
        
        return practices[:limit]
    
    def update_practice_performance(
        self,
        practice_id: str,
        performance_metrics: Dict[str, float],
        success: bool
    ):
        """Update a practice's performance metrics after usage."""
        # Get current practice
        result = self.db.supabase.table(self.table_name).select("*").eq(
            "id", practice_id
        ).execute()
        
        if not result.data:
            return
        
        current = result.data[0]
        current_metrics = json.loads(current.get("performance_metrics", "{}"))
        
        # Merge metrics (weighted average)
        for key, value in performance_metrics.items():
            if key in current_metrics:
                # Weighted average: 70% old, 30% new
                current_metrics[key] = (current_metrics[key] * 0.7) + (value * 0.3)
            else:
                current_metrics[key] = value
        
        # Recalculate success score
        success_score = self._calculate_success_score(current_metrics)
        
        # Update
        self.db.supabase.table(self.table_name).update({
            "performance_metrics": json.dumps(current_metrics),
            "success_score": success_score,
            "usage_count": current.get("usage_count", 0) + 1,
            "success_count": current.get("success_count", 0) + (1 if success else 0),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", practice_id).execute()
    
    def get_top_practices(
        self,
        category: str,
        limit: int = 10
    ) -> List[BestPractice]:
        """Get top-performing practices in a category."""
        result = self.db.supabase.table(self.table_name).select("*").eq(
            "category", category
        ).order("success_score", desc=True).limit(limit).execute()
        
        practices = []
        for row in result.data or []:
            practices.append(BestPractice(
                id=row["id"],
                category=row["category"],
                content=row["content"],
                performance_metrics=json.loads(row.get("performance_metrics", "{}")),
                context=json.loads(row.get("context", "{}")),
                success_score=row["success_score"],
                usage_count=row.get("usage_count", 0),
                success_count=row.get("success_count", 0),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                tags=row.get("tags", [])
            ))
        
        return practices
    
    def _calculate_success_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall success score from metrics."""
        # Weighted combination of key metrics
        weights = {
            "open_rate": 0.2,
            "reply_rate": 0.3,
            "meeting_rate": 0.4,
            "conversion_rate": 0.1
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_relevance(
        self,
        practice_context: Dict[str, Any],
        query_context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score between practice and query contexts."""
        relevance = 0.0
        matches = 0
        
        # Match on key context fields
        context_keys = ["industry", "company_size", "acv_range", "job_title", "region"]
        
        for key in context_keys:
            if key in practice_context and key in query_context:
                if practice_context[key] == query_context[key]:
                    relevance += 0.2
                    matches += 1
        
        # Bonus for exact context match
        if matches == len(context_keys):
            relevance = 1.0
        elif matches > 0:
            relevance = min(relevance, 1.0)
        else:
            relevance = 0.5  # Default relevance if no matches
        
        return relevance


def get_rag_system() -> RAGSystem:
    """Get singleton RAG system instance."""
    global _rag_system_instance
    if '_rag_system_instance' not in globals():
        from ..tools.db_tools import SupabaseDB
        _rag_system_instance = RAGSystem(SupabaseDB())
    return _rag_system_instance






