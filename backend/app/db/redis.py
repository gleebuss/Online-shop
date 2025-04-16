import redis.asyncio as redis

REDIS_HOST = "redis"
REDIS_PORT = 6379
POPULAR_KEY = "popular_products"

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def get_redis() -> redis.Redis:
    return redis_client

async def add_popular_product(product_id: int, score: float = 1.0):
    await redis_client.zincrby(POPULAR_KEY, score, str(product_id))

async def get_popular_products(limit: int = 10):
    return await redis_client.zrevrange(POPULAR_KEY, 0, limit - 1)

async def set_cart(customer_id: int, cart_data: dict):
    key = f"cart:{customer_id}"
    await redis_client.set(key, json.dumps(cart_data))

async def get_cart(customer_id: int) -> dict | None:
    key = f"cart:{customer_id}"
    value = await redis_client.get(key)
    return json.loads(value) if value else None

async def clear_cart(customer_id: int):
    key = f"cart:{customer_id}"
    await redis_client.delete(key)

async def cache_product(product_id: int, product_data: dict, ttl: int = 300):
    key = f"product_cache:{product_id}"
    await redis_client.set(key, json.dumps(product_data), ex=ttl)

async def get_cached_product(product_id: int) -> dict | None:
    key = f"product_cache:{product_id}"
    value = await redis_client.get(key)
    return json.loads(value) if value else None

async def cache_order(order_id: int, order_data: dict, ttl: int = 300):
    key = f"order_cache:{order_id}"
    await redis_client.set(key, json.dumps(order_data), ex=ttl)

async def get_cached_order(order_id: int) -> dict | None:
    key = f"order_cache:{order_id}"
    value = await redis_client.get(key)
    return json.loads(value) if value else None

