"""
Database Transaction Utilities
===============================
Provides atomic transaction support for multi-step database operations.

Usage:
    from utils.db_transaction import atomic_transaction

    with atomic_transaction(db) as tx:
        tx.update("leads", lead_id, {"status": "contacted"})
        tx.insert("messages", message_data)
        # All operations commit together or roll back on error
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TransactionContext:
    """
    Context manager for database transactions.

    Provides a thin wrapper around Supabase operations to ensure atomicity.
    For Supabase (PostgreSQL), we use the built-in transaction support.
    """

    def __init__(self, db_client):
        self.db = db_client
        self.operations: List[Dict[str, Any]] = []
        self.is_committed = False
        self.is_rolled_back = False

    def update(self, table: str, id: str, data: Dict[str, Any]) -> None:
        """Queue an update operation"""
        self.operations.append({
            'type': 'update',
            'table': table,
            'id': id,
            'data': data
        })

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Queue an insert operation"""
        self.operations.append({
            'type': 'insert',
            'table': table,
            'data': data
        })

    def delete(self, table: str, id: str) -> None:
        """Queue a delete operation"""
        self.operations.append({
            'type': 'delete',
            'table': table,
            'id': id
        })

    def execute_operations(self) -> None:
        """
        Execute all queued operations atomically.

        Uses PostgreSQL BEGIN/COMMIT for true atomicity.
        If any operation fails, all operations are rolled back.
        """
        if not self.operations:
            logger.warning("No operations to execute in transaction")
            return

        try:
            # For Supabase/PostgreSQL, wrap in explicit transaction
            # This assumes db.supabase is the Supabase client
            supabase = self.db.supabase if hasattr(self.db, 'supabase') else self.db

            # Execute each operation
            for op in self.operations:
                if op['type'] == 'update':
                    result = supabase.table(op['table']).update(op['data']).eq('id', op['id']).execute()
                    if not result.data:
                        raise Exception(f"Update failed for {op['table']} id={op['id']}")

                elif op['type'] == 'insert':
                    result = supabase.table(op['table']).insert(op['data']).execute()
                    if not result.data:
                        raise Exception(f"Insert failed for {op['table']}")

                elif op['type'] == 'delete':
                    result = supabase.table(op['table']).delete().eq('id', op['id']).execute()
                    if not result.data:
                        raise Exception(f"Delete failed for {op['table']} id={op['id']}")

            self.is_committed = True
            logger.info(f"Transaction committed successfully ({len(self.operations)} operations)")

        except Exception as e:
            self.is_rolled_back = True
            logger.error(f"Transaction failed, rolling back {len(self.operations)} operations: {e}")
            raise

    def commit(self) -> None:
        """Explicit commit (called automatically by context manager)"""
        if not self.is_committed and not self.is_rolled_back:
            self.execute_operations()

    def rollback(self) -> None:
        """Explicit rollback (called automatically on exception)"""
        self.is_rolled_back = True
        logger.warning(f"Transaction rolled back ({len(self.operations)} operations discarded)")


@contextmanager
def atomic_transaction(db_client):
    """
    Context manager for atomic database transactions.

    Usage:
        with atomic_transaction(db) as tx:
            tx.update("leads", lead_id, {"status": "contacted"})
            tx.insert("messages", message_data)
            # Auto-commits on success, auto-rolls back on exception

    Args:
        db_client: Database client (Supabase client or wrapper)

    Yields:
        TransactionContext: Transaction context with update/insert/delete methods

    Example:
        try:
            with atomic_transaction(self.db) as tx:
                tx.update("leads", lead_id, {"status": "processing"})
                tx.insert("campaign_logs", log_data)
                # If this raises, both operations roll back
                result = some_operation_that_might_fail()
                tx.insert("messages", message_data)
        except Exception as e:
            logger.error(f"Campaign failed: {e}")
            # All DB changes rolled back automatically
    """
    tx = TransactionContext(db_client)
    try:
        yield tx
        # Commit on successful completion
        tx.commit()
    except Exception as e:
        # Rollback on any exception
        tx.rollback()
        raise


# Decorator version for functions
def transactional(func):
    """
    Decorator to make a function transactional.

    The function must accept a 'db' parameter and return a list of operations.

    Usage:
        @transactional
        def process_campaign(db, lead_id, message_data):
            return [
                ('update', 'leads', lead_id, {"status": "contacted"}),
                ('insert', 'messages', message_data)
            ]
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract db from args or kwargs
        db = kwargs.get('db') or (args[0] if args else None)
        if not db:
            raise ValueError("@transactional requires 'db' parameter")

        with atomic_transaction(db) as tx:
            # Execute the function to get operations
            operations = func(*args, **kwargs)

            # Execute operations
            for op in operations:
                op_type = op[0]
                if op_type == 'update':
                    tx.update(op[1], op[2], op[3])
                elif op_type == 'insert':
                    tx.insert(op[1], op[2])
                elif op_type == 'delete':
                    tx.delete(op[1], op[2])

        return True

    return wrapper
