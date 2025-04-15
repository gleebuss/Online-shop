import redis.asyncio as redis

REDIS_HOST = "redis"
REDIS_PORT = 6379

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def get_redis() -> redis.Redis:
    return redis_client
