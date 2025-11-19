"""
Redis Queue Utility

Adds message jobs to Redis queue for the Node.js worker to process.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
try:
    from redis import Redis
except ImportError:
    # Fallback if redis not installed
    Redis = None
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis connection (lazy)
redis_client: Optional[Redis] = None

def _get_redis_client() -> Optional[Redis]:
    """Get Redis client, initializing if needed."""
    global redis_client
    if redis_client is None and Redis is not None:
        try:
            redis_client = Redis(
                host=os.getenv("REDIS_HOST", "127.0.0.1"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True
            )
        except Exception as e:
            print(f"Redis connection error: {e}")
            return None
    return redis_client

QUEUE_NAME = os.getenv("REDIS_SCHEDULER_QUEUE", "message_scheduler_queue")


def add_message_job(message_data: Dict[str, Any]) -> bool:
    """
    Add a message job to Redis queue using BullMQ format.
    
    The Node.js worker will pick this up and send the message.
    
    BullMQ stores jobs in Redis with this structure:
    - Key: {queue}:waiting (list)
    - Value: JSON string with job data
    
    The worker expects job.data to contain the message data directly.
    """
    client = _get_redis_client()
    if not client:
        print("Redis not available - message not queued")
        return False
    
    try:
        # BullMQ job format (simplified - BullMQ adds metadata)
        # When using BullMQ Queue.add(), it wraps this, but we're manually pushing
        # So we need to match what BullMQ expects internally
        
        # BullMQ internal format (simplified):
        # The worker receives job.data directly, so we push the message_data
        # BullMQ will wrap it with job metadata
        
        # Use BullMQ's Queue.add() if available, otherwise manual push
        try:
            from bullmq import Queue
            # If bullmq Python package is available, use it
            queue = Queue(QUEUE_NAME, connection=client)
            queue.add("send_message", message_data, {
                "attempts": 3,
                "backoff": {
                    "type": "exponential",
                    "delay": 2000
                }
            })
            return True
        except ImportError:
            # Fallback: Manual push (matches BullMQ format)
            # BullMQ stores jobs as: {queue}:waiting list with JSON strings
            # Format: {"name": "job_name", "data": {...}, "opts": {...}, "id": "...", "timestamp": ...}
            import uuid
            job_id = str(uuid.uuid4())
            job_payload = {
                "name": "send_message",
                "data": message_data,
                "opts": {
                    "attempts": 3,
                    "backoff": {
                        "type": "exponential",
                        "delay": 2000
                    },
                    "jobId": job_id
                },
                "id": job_id,
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            
            # Push to BullMQ waiting list
            client.lpush(f"{QUEUE_NAME}:waiting", json.dumps(job_payload))
            
            return True
        
    except Exception as e:
        print(f"Error adding message job to queue: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_queue_length() -> int:
    """Get the number of jobs waiting in the queue."""
    client = _get_redis_client()
    if not client:
        return 0
    
    try:
        return client.llen(f"{QUEUE_NAME}:waiting")
    except:
        return 0

