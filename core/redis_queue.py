import json
import redis
from config.settings import Settings

class RedisQueue:
    """
    Simple Redis Queue for handling video/pdf processing tasks.
    Uses RPUSH for enqueue and LPOP for dequeue.
    """

    def __init__(self, queue_name="bot_jobs"):
        self.queue_name = queue_name
        self.redis = redis.Redis.from_url(Settings.REDIS_URL, decode_responses=True)

    # ----------------------------------------------------------
    # ADD JOB TO QUEUE
    # ----------------------------------------------------------
    def push(self, data: dict):
        """
        Add a new job to Redis queue.
        Data must be a dict containing:
        {
            'file_id': str,
            'file_type': 'video' | 'pdf',
            'caption': str,
            'title': str,
            'user_id': int
        }
        """
        self.redis.rpush(self.queue_name, json.dumps(data))

    # ----------------------------------------------------------
    # POP JOB FROM QUEUE
    # ----------------------------------------------------------
    def pop(self):
        """
        Fetch next job from queue.
        Returns dict or None if empty.
        """
        item = self.redis.lpop(self.queue_name)
        if item is None:
            return None
        return json.loads(item)

    # ----------------------------------------------------------
    # QUEUE LENGTH
    # ----------------------------------------------------------
    def size(self):
        return self.redis.llen(self.queue_name)

    # ----------------------------------------------------------
    # CLEAR QUEUE
    # ----------------------------------------------------------
    def clear(self):
        self.redis.delete(self.queue_name)


# Global queue object for import anywhere
queue = RedisQueue()
