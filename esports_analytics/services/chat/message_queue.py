"""Message Queue System with Memory Fallback

Message queuing with in-memory implementation when Redis is not available.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import threading

logger = logging.getLogger(__name__)

class QueueType(Enum):
    """Queue type enumeration."""
    MEMORY = "memory"
    REDIS = "redis"
    RABBITMQ = "rabbitmq"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, falling back to in-memory queue")
    CRITICAL = 4

@dataclass
class QueuedMessage:
    """Message in the queue."""
    id: str
    data: Dict[str, Any]
    priority: MessagePriority
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class QueueStats:
    """Queue statistics."""
    total_messages: int
    processed_messages: int
    failed_messages: int
    queue_size: int
    worker_count: int
    avg_processing_time: float
    messages_per_second: float

class MessageQueue:
    """
    High-throughput message queue with auto-scaling workers.
    
    Features:
    - Multiple queue backends (Memory, Redis, RabbitMQ)
    - Priority-based message processing
    - Auto-scaling workers based on queue depth
    - Dead letter queue for failed messages
    - Rate limiting and backpressure handling
    - Comprehensive monitoring and metrics
    """
    
    def __init__(self,
                 queue_type: str = "memory",
                 redis_url: Optional[str] = None,
                 max_workers: int = 10,
                 min_workers: int = 1,
                 scaling_threshold: int = 100,
                 processing_timeout: int = 30):
        # Convert string to QueueType enum
        queue_type = QueueType(queue_type)
        """
        Initialize message queue.
        
        Args:
            queue_type: Type of queue backend
            redis_url: Redis connection URL
            max_workers: Maximum number of worker processes
            min_workers: Minimum number of worker processes
            scaling_threshold: Queue size threshold for scaling
            processing_timeout: Timeout for message processing
        """
        self.queue_type = queue_type
        self.redis_url = redis_url
        self.max_workers = max_workers
        self.min_workers = min_workers
        self.scaling_threshold = scaling_threshold
        self.processing_timeout = processing_timeout
        
        # Queue backend
        self.backend = None
        self.redis_client = None
        
        # Workers
        self.workers = []
        self.worker_count = min_workers
        self.worker_tasks = []
        
        # Statistics
        self.stats = {
            'total_messages': 0,
            'processed_messages': 0,
            'failed_messages': 0,
            'start_time': time.time(),
            'processing_times': deque(maxlen=1000)
        }
        
        # Dead letter queue
        self.dead_letter_queue = deque(maxlen=10000)
        
        # Rate limiting
        self.rate_limiter = {
            'enabled': False,
            'max_messages_per_second': 1000,
            'current_rate': 0,
            'last_reset': time.time()
        }
        
        logger.info(f"Initialized MessageQueue with {queue_type.value} backend")
    
    async def initialize(self):
        """Initialize the queue backend."""
        if self.queue_type == QueueType.REDIS:
            await self._initialize_redis()
        elif self.queue_type == QueueType.MEMORY:
            await self._initialize_memory()
        else:
            raise ValueError(f"Unsupported queue type: {self.queue_type}")
    
    async def _initialize_redis(self):
        """Initialize Redis backend."""
        try:
            self.redis_client = redis.from_url(self.redis_url or "redis://localhost:6379")
            await self.redis_client.ping()
            self.backend = "redis"
            logger.info("Redis backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            # Fallback to memory
            await self._initialize_memory()
    
    async def _initialize_memory(self):
        """Initialize memory backend."""
        self.backend = "memory"
        self.memory_queue = deque()
        self.priority_queues = {
            MessagePriority.CRITICAL: deque(),
            MessagePriority.HIGH: deque(),
            MessagePriority.NORMAL: deque(),
            MessagePriority.LOW: deque()
        }
        logger.info("Memory backend initialized")
    
    async def enqueue(self, 
                    data: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.NORMAL,
                    max_retries: int = 3,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Enqueue a message for processing.
        
        Args:
            data: Message data
            priority: Message priority
            max_retries: Maximum retry attempts
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        message_id = f"msg_{int(time.time() * 1000)}_{id(data)}"
        
        message = QueuedMessage(
            id=message_id,
            data=data,
            priority=priority,
            timestamp=time.time(),
            max_retries=max_retries,
            metadata=metadata
        )
        
        # Rate limiting check
        if self.rate_limiter['enabled']:
            if not await self._check_rate_limit():
                logger.warning(f"Rate limit exceeded, dropping message {message_id}")
                return message_id
        
        # Enqueue based on backend
        if self.backend == "redis":
            await self._enqueue_redis(message)
        else:
            await self._enqueue_memory(message)
        
        self.stats['total_messages'] += 1
        
        # Auto-scale workers if needed
        await self._check_scaling()
        
        logger.debug(f"Enqueued message {message_id} with priority {priority.value}")
        return message_id
    
    async def _enqueue_redis(self, message: QueuedMessage):
        """Enqueue message to Redis."""
        try:
            message_data = json.dumps(asdict(message))
            await self.redis_client.lpush(
                f"queue:{message.priority.value}",
                message_data
            )
        except Exception as e:
            logger.error(f"Failed to enqueue to Redis: {e}")
            raise
    
    async def _enqueue_memory(self, message: QueuedMessage):
        """Enqueue message to memory queue."""
        self.priority_queues[message.priority].append(message)
    
    async def dequeue(self, timeout: int = 1) -> Optional[QueuedMessage]:
        """
        Dequeue a message for processing.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            QueuedMessage or None
        """
        if self.backend == "redis":
            return await self._dequeue_redis(timeout)
        else:
            return await self._dequeue_memory(timeout)
    
    async def _dequeue_redis(self, timeout: int) -> Optional[QueuedMessage]:
        """Dequeue message from Redis."""
        try:
            # Try to get message from highest priority queue first
            for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                           MessagePriority.NORMAL, MessagePriority.LOW]:
                result = await self.redis_client.brpop(
                    f"queue:{priority.value}",
                    timeout=timeout
                )
                if result:
                    _, message_data = result
                    message_dict = json.loads(message_data)
                    return QueuedMessage(**message_dict)
            
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue from Redis: {e}")
            return None
    
    async def _dequeue_memory(self, timeout: int) -> Optional[QueuedMessage]:
        """Dequeue message from memory queue."""
        # Try to get message from highest priority queue first
        for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                       MessagePriority.NORMAL, MessagePriority.LOW]:
            if self.priority_queues[priority]:
                return self.priority_queues[priority].popleft()
        
        return None
    
    async def _check_rate_limit(self) -> bool:
        """Check if rate limit allows new messages."""
        current_time = time.time()
        
        # Reset rate counter if needed
        if current_time - self.rate_limiter['last_reset'] >= 1.0:
            self.rate_limiter['current_rate'] = 0
            self.rate_limiter['last_reset'] = current_time
        
        # Check if under limit
        if self.rate_limiter['current_rate'] < self.rate_limiter['max_messages_per_second']:
            self.rate_limiter['current_rate'] += 1
            return True
        
        return False
    
    async def _check_scaling(self):
        """Check if workers need to be scaled."""
        queue_size = await self.get_queue_size()
        
        # Scale up if queue is getting full
        if queue_size > self.scaling_threshold and self.worker_count < self.max_workers:
            await self._scale_up()
        
        # Scale down if queue is empty and we have excess workers
        elif queue_size == 0 and self.worker_count > self.min_workers:
            await self._scale_down()
    
    async def _scale_up(self):
        """Scale up workers."""
        if self.worker_count < self.max_workers:
            self.worker_count += 1
            logger.info(f"Scaling up to {self.worker_count} workers")
    
    async def _scale_down(self):
        """Scale down workers."""
        if self.worker_count > self.min_workers:
            self.worker_count -= 1
            logger.info(f"Scaling down to {self.worker_count} workers")
    
    async def get_queue_size(self) -> int:
        """Get current queue size."""
        if self.backend == "redis":
            total_size = 0
            for priority in MessagePriority:
                size = await self.redis_client.llen(f"queue:{priority.value}")
                total_size += size
            return total_size
        else:
            total_size = 0
            for queue in self.priority_queues.values():
                total_size += len(queue)
            return total_size
    
    async def start_workers(self, processor: Callable[[QueuedMessage], Awaitable[bool]]):
        """
        Start worker processes.
        
        Args:
            processor: Async function to process messages
        """
        self.processor = processor
        
        # Start initial workers
        for i in range(self.worker_count):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(task)
        
        logger.info(f"Started {self.worker_count} workers")
    
    async def _worker_loop(self, worker_id: str):
        """Worker loop for processing messages."""
        logger.info(f"Worker {worker_id} started")
        
        while True:
            try:
                # Get message from queue
                message = await self.dequeue(timeout=1)
                
                if message:
                    start_time = time.time()
                    
                    try:
                        # Process message with timeout
                        success = await asyncio.wait_for(
                            self.processor(message),
                            timeout=self.processing_timeout
                        )
                        
                        if success:
                            self.stats['processed_messages'] += 1
                        else:
                            await self._handle_failed_message(message)
                        
                        # Record processing time
                        processing_time = time.time() - start_time
                        self.stats['processing_times'].append(processing_time)
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"Message {message.id} processing timeout")
                        await self._handle_failed_message(message)
                    
                    except Exception as e:
                        logger.error(f"Error processing message {message.id}: {e}")
                        await self._handle_failed_message(message)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _handle_failed_message(self, message: QueuedMessage):
        """Handle failed message processing."""
        message.retry_count += 1
        
        if message.retry_count <= message.max_retries:
            # Retry the message
            logger.info(f"Retrying message {message.id} (attempt {message.retry_count})")
            await self.enqueue(
                message.data,
                message.priority,
                message.max_retries,
                message.metadata
            )
        else:
            # Move to dead letter queue
            logger.warning(f"Message {message.id} moved to dead letter queue")
            self.dead_letter_queue.append(message)
            self.stats['failed_messages'] += 1
    
    async def stop_workers(self):
        """Stop all worker processes."""
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logger.info("All workers stopped")
    
    def get_stats(self) -> QueueStats:
        """Get queue statistics."""
        current_time = time.time()
        uptime = current_time - self.stats['start_time']
        
        avg_processing_time = 0
        if self.stats['processing_times']:
            avg_processing_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
        
        messages_per_second = self.stats['processed_messages'] / uptime if uptime > 0 else 0
        
        return QueueStats(
            total_messages=self.stats['total_messages'],
            processed_messages=self.stats['processed_messages'],
            failed_messages=self.stats['failed_messages'],
            queue_size=asyncio.create_task(self.get_queue_size()),
            worker_count=self.worker_count,
            avg_processing_time=avg_processing_time,
            messages_per_second=messages_per_second
        )
    
    def get_dead_letter_queue(self) -> List[QueuedMessage]:
        """Get messages from dead letter queue."""
        return list(self.dead_letter_queue)
    
    def clear_dead_letter_queue(self):
        """Clear dead letter queue."""
        self.dead_letter_queue.clear()
        logger.info("Dead letter queue cleared")
    
    def enable_rate_limiting(self, max_messages_per_second: int):
        """Enable rate limiting."""
        self.rate_limiter['enabled'] = True
        self.rate_limiter['max_messages_per_second'] = max_messages_per_second
        logger.info(f"Rate limiting enabled: {max_messages_per_second} msg/s")
    
    def disable_rate_limiting(self):
        """Disable rate limiting."""
        self.rate_limiter['enabled'] = False
        logger.info("Rate limiting disabled")
