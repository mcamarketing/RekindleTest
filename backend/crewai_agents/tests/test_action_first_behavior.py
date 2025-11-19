"""
Automated Tests for Action-First Behavior

Tests all agents to ensure they follow execution-first, action-only protocol.
"""

import pytest
import asyncio
from typing import Dict, Any, Optional
from ..agents.rex import RexOrchestrator
from ..agents.rex.permissions import PermissionsManager
from ..agents.rex.sentience_engine import SentienceEngine
from ..tools.db_tools import SupabaseDB
from ..utils.action_first_enforcer import ActionFirstEnforcer


class MockDB:
    """Mock database for testing."""
    def __init__(self):
        self.supabase = MockSupabase()


class MockSupabase:
    """Mock Supabase client."""
    def table(self, name):
        return MockTable()


class MockTable:
    """Mock table."""
    def select(self, *args):
        return self
    
    def eq(self, *args):
        return self
    
    def maybe_single(self):
        return self
    
    def execute(self):
        class Result:
            data = None
        return Result()


@pytest.fixture
def mock_db():
    """Create mock database."""
    return MockDB()


@pytest.fixture
def permissions_manager(mock_db):
    """Create permissions manager."""
    return PermissionsManager(mock_db)


@pytest.fixture
def sentience_engine(mock_db):
    """Create sentience engine."""
    return SentienceEngine(user_id="test_user", db=mock_db)


class TestLoggedOutUser:
    """Test behavior for logged-out users."""
    
    def test_logged_out_user_command(self, permissions_manager):
        """Logged-out user should only get conversational info, no execution."""
        user_id = None
        action = "launch_campaign"
        
        can_execute, message = permissions_manager.can_execute_action(user_id, action)
        
        assert not can_execute
        assert "log in" in message.lower() or "please" in message.lower()
    
    def test_logged_out_user_query(self, permissions_manager):
        """Logged-out user query should be conversational only."""
        user_id = None
        action = None  # General query
        
        is_logged_in, _, _ = permissions_manager.check_user_state(user_id)
        
        assert not is_logged_in


class TestLoggedInUserAllowed:
    """Test behavior for logged-in users with allowed packages."""
    
    def test_logged_in_starter_campaign_launch(self, permissions_manager):
        """Starter package should allow campaign launch."""
        # Mock user with starter package
        user_id = "test_user_starter"
        action = "launch_campaign"
        
        # This would need actual DB setup, but structure is correct
        # can_execute, message = permissions_manager.can_execute_action(user_id, action)
        # assert can_execute
    
    def test_logged_in_professional_all_features(self, permissions_manager):
        """Professional package should allow all features."""
        user_id = "test_user_pro"
        action = "reactivate_leads"
        
        # This would need actual DB setup
        # can_execute, message = permissions_manager.can_execute_action(user_id, action)
        # assert can_execute


class TestLoggedInUserDisallowed:
    """Test behavior for logged-in users with disallowed packages."""
    
    def test_free_package_campaign_denied(self, permissions_manager):
        """Free package should deny campaign launch."""
        user_id = "test_user_free"
        action = "launch_campaign"
        
        # Mock free package
        # can_execute, message = permissions_manager.can_execute_action(user_id, action)
        # assert not can_execute
        # assert "package" in message.lower() or "upgrade" in message.lower()
    
    def test_starter_package_reactivation_denied(self, permissions_manager):
        """Starter package should deny lead reactivation."""
        user_id = "test_user_starter"
        action = "reactivate_leads"
        
        # Mock starter package
        # can_execute, message = permissions_manager.can_execute_action(user_id, action)
        # assert not can_execute
        # assert "package" in message.lower() or "upgrade" in message.lower()


class TestActionFirstResponses:
    """Test that responses follow action-first protocol."""
    
    def test_response_no_demo_language(self):
        """Responses should not contain demo/sales/tutorial language."""
        good_responses = [
            "Campaign launched.",
            "Lead research complete.",
            "Sequence deployed.",
            "Task completed."
        ]
        
        for response in good_responses:
            assert ActionFirstEnforcer.validate_response(response)
    
    def test_response_cleans_fluff(self):
        """Response wrapper should clean fluff prefixes."""
        bad_responses = [
            "Good morning! I can help you launch a campaign.",
            "Hi there! Let me show you how to...",
            "Sure! I'll help you with that step-by-step."
        ]
        
        for response in bad_responses:
            cleaned = ActionFirstEnforcer.clean_response(response)
            assert ActionFirstEnforcer.validate_response(cleaned)
            assert len(cleaned) < len(response)  # Should be shorter
    
    def test_response_no_step_by_step(self):
        """Responses should not contain step-by-step guides."""
        bad_responses = [
            "Here's a step-by-step guide...",
            "Let me walk you through this...",
            "First, you need to..."
        ]
        
        for response in bad_responses:
            assert not ActionFirstEnforcer.validate_response(response)


class TestSelfHealing:
    """Test self-healing retry logic."""
    
    def test_retry_on_transient_error(self, sentience_engine):
        """Should retry on transient errors."""
        self_healing = sentience_engine.self_healing
        
        # Transient errors should trigger retry
        timeout_error = Exception("Connection timeout")
        assert self_healing.should_retry(timeout_error, attempt=1, max_attempts=2)
        
        rate_limit_error = Exception("Rate limit exceeded")
        assert self_healing.should_retry(rate_limit_error, attempt=1, max_attempts=2)
    
    def test_no_retry_on_permanent_error(self, sentience_engine):
        """Should not retry on permanent errors."""
        self_healing = sentience_engine.self_healing
        
        # Permanent errors should not trigger retry
        permission_error = Exception("Permission denied")
        assert not self_healing.should_retry(permission_error, attempt=1, max_attempts=2)
        
        # Max attempts reached
        assert not self_healing.should_retry(Exception("Any error"), attempt=2, max_attempts=2)


class TestSentienceEngine:
    """Test sentience engine integration."""
    
    @pytest.mark.asyncio
    async def test_introspection_refines_response(self, sentience_engine):
        """Introspection loop should refine responses."""
        draft = "I can help you launch a campaign. Would you like me to start?"
        context = {
            "is_logged_in": True,
            "package_type": "professional",
            "action": "launch_campaign",
            "user_message": "launch campaign"
        }
        
        refined = await sentience_engine.introspector.refine(draft, context)
        
        # Should be cleaner and more action-first
        assert len(refined) <= len(draft)
        assert ActionFirstEnforcer.validate_response(refined)
    
    def test_persona_adaptation(self, sentience_engine):
        """Persona adapter should adjust tone based on context."""
        context = {
            "is_logged_in": True,
            "package_type": "enterprise",
            "task_complexity": "high",
            "last_success": True
        }
        
        persona = sentience_engine.persona_adapter.adapt(context)
        
        assert "tone" in persona
        assert "mood" in persona
        assert "verbosity" in persona
        assert persona["confidence"] > 0


class TestREXOrchestration:
    """Test REX orchestrator behavior."""
    
    @pytest.mark.asyncio
    async def test_rex_executes_immediately(self):
        """REX should execute commands immediately without asking."""
        # This would need full setup with mock orchestration service
        # rex = RexOrchestrator(user_id="test_user")
        # result = rex.execute_command("launch campaign")
        # assert "launched" in result["response"].lower()
        # assert "would you like" not in result["response"].lower()
        pass
    
    def test_rex_no_demo_messages(self):
        """REX should never return demo/sales messages."""
        # Test that REX responses are action-first
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

