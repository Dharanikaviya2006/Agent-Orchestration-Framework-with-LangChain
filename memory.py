import redis
import os
import json

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def save_memory(session_id: str, data: dict):
    redis_client.set(session_id, json.dumps(data))

def load_memory(session_id: str):
    data = redis_client.get(session_id)
    if data:
        return json.loads(data)
    return {}
