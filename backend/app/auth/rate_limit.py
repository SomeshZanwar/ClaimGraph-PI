from __future__ import annotations

from functools import lru_cache

from redis import Redis

from app.config import get_settings


class RateLimitExceeded(RuntimeError):
    def __init__(self, retry_after: int) -> None:
        super().__init__("Rate limit exceeded")
        self.retry_after = max(retry_after, 1)


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def enforce_rate_limit(
    key: str,
    *,
    limit: int,
    window_seconds: int,
) -> None:
    redis_client = get_redis_client()

    with redis_client.pipeline() as pipe:
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl = pipe.execute()

    if int(count) == 1 or int(ttl) < 0:
        redis_client.expire(key, window_seconds)
        ttl = window_seconds

    if int(count) > limit:
        raise RateLimitExceeded(int(ttl))
